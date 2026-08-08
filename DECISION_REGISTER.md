# Decision Register: ComfyUI-CMF Integration

- **Repository:** `ComfyUI-CMF` (Cortiq Model Format Custom Nodes for ComfyUI)
- **Status:** Approved & Codified
- **Last Updated:** 2026-08-08

This document serves as the durable Architecture Decision Record (ADR) and decision register for the `ComfyUI-CMF` integration. All architectural choices, technical constraints, FFI contracts, and memory safety rules are recorded here for auditing and future maintainers.

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

---

## Detailed Decision Records

### DR-001 - Direct C-FFI via `ctypes` over HTTP Daemon

- **Date:** 2026-08-08
- **Status:** Accepted
- **Decision:** Load the compiled Rust FFI library (`cortiq-ffi`) directly into Python using `ctypes` rather than launching a background `cortiq-server` HTTP daemon process.
- **Rationale:** 
  1. **Zero IPC Overhead:** Eliminates HTTP serialization/deserialization latency for local LLM token generation.
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
- **Rationale:** `cortiq_chat` is a long-running execution loop. `cortiq-ffi` thread-safely supports calling `cortiq_cancel(handle)` from another thread or callback context. Halting generation immediately when the user clicks "Cancel" in ComfyUI prevents GPU/CPU lockup.
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
