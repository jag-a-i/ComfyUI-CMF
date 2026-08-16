# Decision Register: ComfyUI-CMF Integration

- **Repository:** `ComfyUI-CMF` (Cortiq Model Format Custom Nodes for ComfyUI)
- **Status:** Approved & Codified
- **Last Updated:** 2026-08-15

This document serves as the durable Architecture Decision Record (ADR) and decision register for the `ComfyUI-CMF` integration. All architectural choices, technical constraints, FFI contracts, memory safety rules, and GPU kernel designs are recorded here for auditing and future maintainers.

---

## Decision Summary

| ID | Title | Status | Date | Decision Summary |
|---|---|---|---|---|
| [DR-001](#dr-001---direct-c-ffi-via-ctypes-over-http-daemon) | Direct C-FFI via `ctypes` over HTTP Daemon | Accepted | 2026-08-08 | Use Python `ctypes` against `cortiq-ffi` C ABI instead of spawning a local HTTP server. |
| [DR-002](#dr-002---raii-model-handle-wrapper-cmfmodelhandle) | RAII Model Handle Wrapper (`CMFModelHandle`) | Accepted | 2026-08-08 | Encapsulate raw `c_void_p` handles in Python objects with explicit `close()` and `__del__` to call `cortiq_free()`. |
| [DR-003](#dr-003---thread-local-c-error-propagation-via-cortiq_last_error) | Thread-Local C Error Propagation via `cortiq_last_error()` | Accepted | 2026-08-08 | Inspect `cortiq_last_error()` on failed FFI operations and raise descriptive Python `RuntimeError`s. |
| [DR-004](#dr-004---asynchronous-cancellation-via-cortiq_cancel) | Asynchronous Cancellation via `cortiq_cancel()` | Accepted | 2026-08-08 | Intercept ComfyUI interrupt signals during token generation and call `cortiq_cancel(handle)` from Python. |
| [DR-005](#dr-005---c-callback-garbage-collection-protection) | C Callback Garbage Collection Protection | Accepted | 2026-08-08 | Retain strong Python references to `ctypes.CFUNCTYPE` instances during `cortiq_chat` invocation. |
| [DR-006](#dr-006---dynamic-cross-platform-shared-library-resolution) | Dynamic Cross-Platform Shared Library Resolution | Accepted | 2026-08-08 | Auto-detect host OS (`win32`, `linux`, `darwin`) and search for `cortiq_ffi.dll`, `libcortiq_ffi.so`, or `libcortiq_ffi.dylib`. |
| [DR-007](#dr-007---multi-turn-chat-generation-node-cmfchatgenerate) | Multi-Turn Chat Generation Node (`CMFChatGenerate`) | Accepted | 2026-08-08 | Expose `cortiq_chat_messages` as a dedicated node alongside single-turn text generation (`CMFTextGenerate`). |
| [DR-008](#dr-008---automatic-comfyui-model-folder-registration) | Automatic ComfyUI Model Folder Registration | Accepted | 2026-08-08 | Register `ComfyUI/models/cmf/` into ComfyUI's global `folder_paths` registry on module import. |
| [DR-009](#dr-009---3d-parallel-head-wgsl-workgroup-topology) | 3D Parallel Head WGSL Workgroup Topology | Accepted | 2026-08-14 | Dispatch all 32 attention heads concurrently in the $Z$ workgroup dimension (`dispatch_workgroups(gx, gy, 32)`) with native shader head offsets. |
| [DR-010](#dr-010---rejection-of-host-side-slicing-in-favor-of-fused-sram-flashattention) | Rejection of Host Slicing for Fused SRAM FlashAttention | Accepted | 2026-08-14 | Prohibit host CPU chunk loops and 3-pass global VRAM score buffers; mandate single-pass fused FlashAttention in workgroup shared memory. |
| [DR-011](#dr-011---zero-paging-physical-vram-ceiling-policy) | Zero-Paging Physical VRAM Ceiling Policy ($\le 6.5\text{ GB}$) | Accepted | 2026-08-14 | Enforce strict scratch buffer bounds to prevent allocations exceeding physical VRAM and triggering Windows WDDM PCIe paging stalls. |
| [DR-013](#dr-013---native-vulkan-cooperative-matrix-route-for-q4tp-gemm) | Native Vulkan Cooperative Matrix Route for Q4TP GEMM | Accepted | 2026-08-15 | `gpu::q4tp_matmat` prefers `vulkan::q4tp_matmat` (`q4tp_coop.spv` / `VK_KHR_cooperative_matrix`) over scalar WGSL when the f16 16×16 shape is present. |
| [DR-014](#dr-014---2d-tiled-sram-flashattention) | 2D Tiled SRAM FlashAttention | Accepted | 2026-08-15 | Replace 3-pass QK→softmax→PV score buffers with a 64×64 workgroup-tiled online softmax (`dit_flash_attend`) that writes no global scores. |
| [DR-015](#dr-015---dit-step-command-buffer-graph) | DiT-Step Command Buffer Graph | Accepted | 2026-08-15 | Pre-record all DiT block encodings and submit them once per step; enable the wgpu resident chain on Windows/Linux discrete cards. |

---

## Detailed Decision Records

### DR-001 - Direct C-FFI via `ctypes` over HTTP Daemon

- **Date:** 2026-08-08
- **Status:** Accepted
- **Decision:** Load the compiled Rust FFI library (`cortiq-ffi`) directly into Python using `ctypes` rather than launching a background `cortiq-server` HTTP daemon process.
- **Rationale:** 
  1. **Zero IPC Overhead:** Eliminates HTTP serialization/deserialization latency for local LLM/diffusion token generation.
  2. **Zero-Copy Memory Mapping:** CMF leverages memory-mapped weights (`mmap`). Direct FFI allows Python to control the handle while Rust accesses physical RAM/VRAM pages natively.
  3. **Process Simplicity:** Prevents zombie background server processes, port collisions, or connection failures inside ComfyUI worker environments.
- **Consequences:** Requires users (or build scripts) to place compiled native binaries (`.dll` / `.so` / `.dylib`) in the node's `bin/` directory.
- **References:** `crates/cortiq-ffi/include/cortiq.h`, `wrapper.py`

---

### DR-002 - RAII Model Handle Wrapper (`CMFModelHandle`)

- **Date:** 2026-08-08
- **Status:** Accepted
- **Decision:** Wrap raw `c_void_p` model pointers returned by `cortiq_load()` inside a Python `CMFModelHandle` class that manages lifecycle and invokes `cortiq_free(handle)` upon garbage collection or node release.
- **Rationale:** The naive implementation in early drafts held raw pointers in global scope without calling `cortiq_free()`. In ComfyUI workflows, users frequently re-run or swap models, causing memory leaks and unreleased file descriptors for mmap files.
- **Consequences:** All node inputs receiving `CMF_MODEL` sockets expect a `CMFModelHandle` instance, guaranteeing clean resource reclamation.
- **References:** `wrapper.py`, `nodes.py`

---

### DR-003 - Thread-Local C Error Propagation via `cortiq_last_error()`

- **Date:** 2026-08-08
- **Status:** Accepted
- **Decision:** Check return codes on all C FFI calls (`cortiq_load`, `cortiq_chat`, `cortiq_set_options`). If `cortiq_load` returns `NULL` or functions return negative codes, invoke `cortiq_last_error()` and raise a Python `RuntimeError` containing the exact Rust diagnostic.
- **Rationale:** Raw C FFI crashes silently or returns generic `NULL` without error propagation. `cortiq-ffi` exports a thread-local error string accessor (`cortiq_last_error()`). Exposing this string to ComfyUI provides actionable UI error messages (e.g., corrupt `.cmf` file, quantization mismatch, out of memory).
- **Consequences:** Users see precise error dialogs in the ComfyUI frontend when model execution fails.
- **References:** `crates/cortiq-ffi/src/lib.rs`, `wrapper.py`

---

### DR-004 - Asynchronous Cancellation via `cortiq_cancel()`

- **Date:** 2026-08-08
- **Status:** Accepted
- **Decision:** Hook ComfyUI's processing interrupt listener (`comfy.model_management.throw_exception_if_processing_interrupted`) inside the C token streaming callback, calling `cortiq_cancel(handle)` when an interrupt is detected.
- **Rationale:** `cortiq_chat` and `cortiq_image_generate` are long-running execution loops. `cortiq-ffi` thread-safely supports calling `cortiq_cancel(handle)` from another thread or callback context. Halting generation immediately when the user clicks "Cancel" in ComfyUI prevents GPU/CPU lockup.
- **Consequences:** Responsive cancellation behavior in ComfyUI without crashing the Python process or Rust runtime.
- **References:** `crates/cortiq-ffi/include/cortiq.h`, `wrapper.py`, `nodes.py`

---

### DR-005 - C Callback Garbage Collection Protection

- **Date:** 2026-08-08
- **Status:** Accepted
- **Decision:** Explicitly assign the `ctypes.CFUNCTYPE` callback object to a local/instance Python variable before passing it to `cortiq_chat()` or `cortiq_chat_messages()`.
- **Rationale:** If a `ctypes` callback function is passed anonymously to a C function, Python's garbage collector may collect the function wrapper during execution, causing C to invoke a dereferenced function pointer resulting in a severe segmentation fault.
- **Consequences:** Guaranteed pointer stability during long streaming generation runs.
- **References:** `wrapper.py`

---

### DR-006 - Dynamic Cross-Platform Shared Library Resolution

- **Date:** 2026-08-08
- **Status:** Accepted
- **Decision:** Implement dynamic path resolution in `CMFWrapper` that inspects `sys.platform` and searches for:
  - `cortiq_ffi.dll` on Windows (`win32`)
  - `libcortiq_ffi.so` on Linux (`linux`)
  - `libcortiq_ffi.dylib` on macOS (`darwin`)
- **Rationale:** Avoids hardcoded file extensions (such as `.so`) which break Windows and macOS installations. Searches both `ComfyUI-CMF/bin/` and system PATH.
- **Consequences:** Seamless cross-platform support out of the box.
- **References:** `wrapper.py`

---

### DR-007 - Multi-Turn Chat Generation Node (`CMFChatGenerate`)

- **Date:** 2026-08-08
- **Status:** Accepted
- **Decision:** Implement `CMFChatGenerate` as a dedicated node in addition to `CMFTextGenerate`. `CMFChatGenerate` accepts JSON-formatted message lists or role pairs and passes them to `cortiq_chat_messages()`.
- **Rationale:** CMF models natively support structured chat templates (Qwen3, Gemma, DeepSeek) via `cortiq_chat_messages()`. Single-turn prompt generation is insufficient for agentic workflows or multi-turn prompt building in ComfyUI.
- **Consequences:** Users can build full conversational AI pipelines inside ComfyUI.
- **References:** `nodes.py`

---

### DR-008 - Automatic ComfyUI Model Folder Registration

- **Date:** 2026-08-08
- **Status:** Accepted
- **Decision:** Automatically register `ComfyUI/models/cmf/` into ComfyUI's `folder_paths` manager on module load, creating the folder if it does not exist.
- **Rationale:** Provides a dedicated directory for `.cmf` models alongside ComfyUI's standard `checkpoints/`, `loras/`, and `vae/` directories, preventing path configuration friction.
- **Consequences:** Users simply drop `.cmf` files into `models/cmf/` and see them in the `CMFModelLoader` dropdown menu.
- **References:** `__init__.py`, `nodes.py`

---

### DR-009 - 3D Parallel Head WGSL Workgroup Topology

- **Date:** 2026-08-14
- **Status:** Accepted
- **Decision:** Parallelize attention heads natively in the $Z$ workgroup grid dimension (`@builtin(workgroup_id).z = head_index`) and dispatch `pass.dispatch_workgroups(gx, gy, 32)` rather than looping over attention heads in host CPU code.
- **Rationale:** Eliminates 130,000+ host driver bind-group invocations per step, dropping 1024x1024 generation from 1,585s down to 256.41s.
- **Consequences:** All downstream WGSL shaders (`dit_qk`, `dit_sm`, `dit_pv`) must use uniform stride parameters (`dp.s0`, `dp.ntok`, `dp.hpk`) for multi-head indexing.
- **References:** `crates/cortiq-engine/src/gpu_wgpu.rs` (commit `221cb5d`)

---

### DR-010 - Rejection of Host Slicing for Fused SRAM FlashAttention

- **Date:** 2026-08-14
- **Status:** Accepted
- **Decision:** Reject multi-pass global VRAM score buffers (`dit_qk` $\rightarrow$ `dit_softmax` $\rightarrow$ `dit_pv`) and host chunk loops in favor of a single fused FlashAttention WGSL shader (`dit_flash_attend`) with online softmax in workgroup shared memory (`var<workgroup>`).
- **Rationale:** The 3-pass unfused architecture moves 212 GB of intermediate score traffic across the VRAM memory bus on every step (4.24 TB total), creating a 256-second bottleneck. Fused SRAM attention reduces global score traffic to 0 MB.
- **Consequences:** Collapses attention passes from 51 down to 1 per DiT block, enabling sub-20s generation targets.
- **References:** `implementation_plan.md`, `crates/cortiq-engine/src/gpu_wgpu.rs`

---

### DR-011 - Zero-Paging Physical VRAM Ceiling Policy

- **Date:** 2026-08-14
- **Status:** Accepted
- **Decision:** Enforce a strict $\le 6.5\text{ GB}$ peak VRAM allocation ceiling across all intermediate buffers on 10GB/12GB GPUs.
- **Rationale:** On Windows WDDM, exceeding physical VRAM triggers silent PCIe paging over the system RAM bus at ~25 GB/s (vs 760 GB/s GDDR6X), causing catastrophic generation freezes (13,933s).
- **Consequences:** Intermediate tile sizes must be bounded and allocated in static scratch memory (`Scratch::ensure`).
- **References:** `crates/cortiq-engine/src/gpu_wgpu.rs`

---

### DR-013 - Native Vulkan Cooperative Matrix Route for Q4TP GEMM

- **Date:** 2026-08-15
- **Status:** Accepted
- **Decision:** Wire standalone Q4TP GEMM projections through `crates/cortiq-engine/src/vulkan.rs` (`q4tp_coop.spv`, `VK_KHR_cooperative_matrix`, f16 16×16 / f32 accumulator) behind `CMF_VK=1`. Default remains wgpu. Do not mix ash and wgpu device memory inside a fused DiT block.
- **Rationale:** The native lane measures 62.8 TFLOP/s against 25.1 TFLOP/s scalar WGSL on the cards it was written for. On this machine the same kernel advertises the shape and still fails `vk_coop` (relative error ~1e4), so auto-routing would silently corrupt projections. Fused-block GEMMs stay on wgpu (which already selects `q4tp_mm_coop` when the adapter reports the shape).
- **Consequences:** `gpu::q4tp_matmat` uses the native lane only when `CMF_VK=1`. The lane still probes for tests. `CMF_VK=0` (or unset) leaves wgpu in charge.
- **References:** `crates/cortiq-engine/src/vulkan.rs`, `crates/cortiq-engine/src/gpu.rs`, `crates/cortiq-engine/tests/vk_coop.rs`

---

### DR-014 - 2D Tiled SRAM FlashAttention

- **Date:** 2026-08-15
- **Status:** Accepted
- **Decision:** For `hd ≤ 128`, replace the 3-pass `dit_qk` → `dit_softmax` → `dit_pv` path (global `scb` score buffer) with a single `dit_flash_attend` dispatch. Each workgroup owns a 64×64 score tile in `var<workgroup>` and runs online softmax; output is written token-major so the unstack pass is skipped.
- **Rationale:** The unfused path writes a full score matrix to VRAM per layer (hundreds of GB of traffic per 1024² render). SRAM tiles drop global score writes to zero (DR-010).
- **Consequences:** Heads wider than 128 keep the 3-pass path. The CPU reference in `tests/flash_attend_2d.rs` is the independent truth for the tiled loop.
- **References:** `crates/cortiq-engine/src/gpu_wgpu.rs` (`dit_flash_attend`, `dit_block_seg`, `dit_attention`)

---

### DR-015 - DiT-Step Command Buffer Graph

- **Date:** 2026-08-15
- **Status:** Accepted
- **Decision:** Record every DiT block encoding into a per-step command-buffer list and submit once (`dit_step_begin` / `dit_step_end`). Enable the wgpu resident hidden-state chain on Windows/Linux discrete cards. The native Vulkan lane holds 32 reusable primary command buffers (`GRAPH_SLOTS`) recorded against `VK_COMMAND_BUFFER_USAGE_SIMULTANEOUS_USE`.
- **Rationale:** A 32-block stack used to open 32 `queue.submit` calls (and, before the chain fix, 32 PCIe readbacks). One submit per step removes the driver tax. `fused_dit_block_available` stays Metal-only so CFG batching in `imagegen.rs` does not change.
- **Consequences:** `dit_chain_supported` now matches the `dit_block_seg` wgpu gate. Readback flushes the stashed graph before mapping.
- **References:** `crates/cortiq-engine/src/gpu.rs`, `crates/cortiq-engine/src/gpu_wgpu.rs`, `crates/cortiq-engine/src/dit.rs`, `crates/cortiq-engine/src/vulkan.rs`
