# ComfyUI-CMF Custom Nodes

High-performance native **Cortiq Model Format (CMF)** LLM & VLM inference integration for [ComfyUI](https://github.com/comfyanonymous/ComfyUI).

CMF leverages memory-mapped weights (`mmap`), 4-bit quantizations, and Vulkan/GPU acceleration to enable ultra-fast, zero-copy local language model execution inside ComfyUI pipelines.

---

## Key Features

- **Direct C-FFI Binding**: Uses Python `ctypes` against `cortiq-ffi` for zero IPC/HTTP server overhead.
- **Instant Model Loading**: Uses native `mmap` for near-instant model load times.
- **Asynchronous Cancellation**: Supports stopping long token generation runs immediately via ComfyUI's "Cancel" button.
- **RAII Memory Safety**: Automatically frees Rust model handles and unmaps file memory when workflows reset or models change.
- **Multi-Turn Chat Support**: Provides dedicated structured chat nodes (`CMFChatGenerate`) supporting System Prompts and Qwen3/Gemma chat templates.
- **Detailed Rust Diagnostics**: Propagates thread-local error messages via `cortiq_last_error()` directly to the ComfyUI frontend.

---

## Directory Structure

```text
ComfyUI/custom_nodes/ComfyUI-CMF/
├── __init__.py          # Node mappings and folder registration
├── wrapper.py           # Python ctypes wrapper & RAII handle manager
├── nodes.py             # ComfyUI custom node implementations
├── bin/                 # Native C-FFI library (cortiq_ffi.dll / .so / .dylib)
├── DECISION_REGISTER.md # Auditable Architecture Decision Record (ADR)
├── docs/
│   └── ARCHITECTURE.md  # Deep-dive architecture specifications
└── README.md            # This document
```

---

## Setup & Installation

### 1. Place Compiled FFI Library
Build or copy the compiled `cortiq-ffi` dynamic library into `custom_nodes/ComfyUI-CMF/bin/`:

* **Windows**: `bin/cortiq_ffi.dll`
* **Linux**: `bin/libcortiq_ffi.so`
* **macOS**: `bin/libcortiq_ffi.dylib`

To build from the `cmf` repository source:
```bash
cargo build -p cortiq-ffi --release
# Copy target/release/cortiq_ffi.dll (or libcortiq_ffi.so) to custom_nodes/ComfyUI-CMF/bin/
```

### 2. Place CMF Model Files
Place your `.cmf` model files in the designated ComfyUI directory:
```text
ComfyUI/models/cmf/
```
*(The `models/cmf/` folder will be created automatically on first run).*

---

## Available Nodes

1. **Load CMF Model (`CMFModelLoader`)**: Selects and memory-maps `.cmf` models from `models/cmf/`.
2. **CMF Sampler Options (`CMFSamplerOptions`)**: Configures temperature, top_p, top_k, repetition penalty, greedy decoding, and seed.
3. **CMF Text Generation (`CMFTextGenerate`)**: Single-turn prompt generation node with streaming output and cancellation support.
4. **CMF Chat Generation (`CMFChatGenerate`)**: Multi-turn structured chat node accepting System Prompt and User Prompt.

---

## Architecture & Design Audit

For detailed architectural decisions, FFI memory contracts, and GIL safety analysis, refer to:
- [DECISION_REGISTER.md](DECISION_REGISTER.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
