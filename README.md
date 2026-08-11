# ComfyUI-CMF Custom Nodes

High-performance native **Cortiq Model Format (CMF)** LLM & VLM inference integration for [ComfyUI](https://github.com/comfyanonymous/ComfyUI).

CMF leverages memory-mapped weights (`mmap`), 4-bit quantizations, and Vulkan/GPU acceleration to enable ultra-fast, zero-copy local language model execution inside ComfyUI pipelines.

---

## Credits & Acknowledgments

This custom node package is an independent extension built for **CMF (Cortiq Model Format)**:
- **Original CMF Repository**: [https://github.com/infosave2007/cmf](https://github.com/infosave2007/cmf)
- **Engine Author**: [@infosave2007](https://github.com/infosave2007)
- **License**: Apache License 2.0

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

### 1. Automatic 1-Step Installation (Recommended)
Simply clone this repository into your ComfyUI `custom_nodes/` directory:

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/jag-a-i/ComfyUI-CMF.git
```

When ComfyUI starts up, `ComfyUI-CMF` will **automatically detect** if the native GPU dynamic library is built and compile it if missing!

### 2. Manual / One-Click Build Script
You can also run the build script manually at any time:
- **Windows**: Double-click `install.bat` or run `python install.py`
- **Linux / macOS**: Run `./install.sh` or `python3 install.py`

*(Requires [Rust/Cargo](https://rustup.rs/) installed on system PATH for native GPU compilation).*


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
