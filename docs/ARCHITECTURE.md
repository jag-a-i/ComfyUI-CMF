# Architecture Specifications: ComfyUI-CMF

- **Component:** `ComfyUI-CMF` (Cortiq Model Format Custom Nodes for ComfyUI)
- **Version:** 1.0.0
- **Target Environment:** Python 3.10+ / PyTorch / ComfyUI / Rust C-FFI (`cortiq-ffi`)

---

## 1. System Context & Overview

`ComfyUI-CMF` integrates the **Cortiq Model Format (CMF)** Rust inference engine into ComfyUI. CMF provides high-performance, low-memory-footprint execution of 4-bit quantized Language Models and Vision-Language Models using native memory mapping (`mmap`) and Vulkan/GPU acceleration.

```
+-----------------------------------------------------------------------+
|                            ComfyUI Engine                             |
+-----------------------------------------------------------------------+
                                   |
        +--------------------------+--------------------------+
        |                                                     |
        v                                                     v
+-------------------------------+             +-------------------------------+
|        CMFModelLoader         |             |       CMFSamplerOptions       |
+---------------+---------------+             +---------------+---------------+
                |                                             |
                | (CMFModelHandle)                            | (JSON String)
                +--------------------------+------------------+
                                           |
                                           v
                            +-------------------------------+
                            |   CMFTextGenerate / CMFChat   |
                            +---------------+---------------+
                                           |
                                           v
                            +-------------------------------+
                            |     CMFWrapper (ctypes)       |
                            +---------------+---------------+
                                           |
                                           | (C ABI Exports)
                                           v
                            +-------------------------------+
                            |   cortiq-ffi dynamic library  |
                            |    (.dll / .so / .dylib)      |
                            +---------------+---------------+
                                           |
                                           v
                            +-------------------------------+
                            |    cortiq-engine (Rust core)  |
                            +-------------------------------+
```

---

## 2. Dynamic Library & FFI Interface Specs

The FFI interface binds to `crates/cortiq-ffi/include/cortiq.h`.

### C Function Signatures Bound via `ctypes`

```c
/* Open a .cmf file (memory-mapped). Returns opaque handle pointer; NULL on error. */
void *cortiq_load(const char *path);

/* Globally enable or disable discrete GPU graph. Must be called before cortiq_load. */
void cortiq_set_gpu(bool enable);

/* Set thread count for multi-threaded inference pool. 0 = auto. */
void cortiq_set_threads(int32_t n);

/* Set runtime JSON options (temperature, top_p, greedy, seed, repetition_penalty). Returns 0 on success, -1 on error. */
int32_t cortiq_set_options(void *handle, const char *json_options);

/* Single turn streaming chat generation. Returns total tokens generated or -1 on error. */
int32_t cortiq_chat(void *handle, const char *prompt, uint32_t max_tokens, cortiq_token_cb cb, void *user);

/* Multi-turn structured JSON message list generation. Returns total tokens or -1 on error. */
int32_t cortiq_chat_messages(void *handle, const char *json_messages, uint32_t max_tokens, cortiq_token_cb cb, void *user);

/* Asynchronously cancel generation running on handle (thread-safe). */
void cortiq_cancel(void *handle);

/* Get thread-local error message from previous failed FFI call. */
const char *cortiq_last_error(void);

/* Get JSON execution environment status {"simd": "neon", "threads": 4, "gpu_backend": true}. */
const char *cortiq_execution_info(void);

/* Free a model handle. NULL is no-op. */
void cortiq_free(void *handle);
```

---

## 3. Python Layer Architecture (`wrapper.py` & `nodes.py`)

### 3.1 Handle Management (`CMFModelHandle`)

Raw C pointers (`c_void_p`) are never exposed directly to ComfyUI nodes. Instead, `cortiq_load()` returns a `CMFModelHandle` instance:

```python
class CMFModelHandle:
    def __init__(self, wrapper: CMFWrapper, handle: int, path: str):
        self.wrapper = wrapper
        self.handle = handle
        self.path = path
        self._closed = False

    def close(self):
        if not self._closed and self.handle:
            self.wrapper.lib.cortiq_free(self.handle)
            self.handle = None
            self._closed = True

    def __del__(self):
        self.close()
```

### 3.2 Threading, GIL & Interruption Flow

When `CMFTextGenerate.generate()` or `CMFChatGenerate.generate()` executes:
1. The node extracts the active `CMFModelHandle`.
2. Python registers a `CFUNCTYPE` callback: `(const char *token, void *user) -> bool`.
3. Inside the callback:
   - Token string is UTF-8 decoded and appended to the output buffer.
   - ComfyUI interruption state is checked via `comfy.model_management.throw_exception_if_processing_interrupted()`.
   - If interrupted, the wrapper calls `cortiq_cancel(handle)` and returns `False` to Rust to halt generation immediately.
4. Python callback wrapper object is held in local scope for the duration of the FFI call to prevent garbage collection.

---

## 4. ComfyUI Node Specifications

### 1. `CMFModelLoader`
- **Inputs:** `model_name` (dropdown of `.cmf` files in `models/cmf/`)
- **Outputs:** `CMF_MODEL` (`CMFModelHandle`)
- **Category:** `Cortiq/CMF`
- **Function:** `load_model`

### 2. `CMFSamplerOptions`
- **Inputs:**
  - `temperature` (FLOAT, default: `0.7`, min: `0.0`, max: `2.0`, step: `0.01`)
  - `top_p` (FLOAT, default: `0.9`, min: `0.0`, max: `1.0`, step: `0.01`)
  - `top_k` (INT, default: `40`, min: `0`, max: `200`)
  - `repetition_penalty` (FLOAT, default: `1.1`, min: `1.0`, max: `2.0`, step: `0.01`)
  - `greedy` (BOOLEAN, default: `False`)
  - `seed` (INT, default: `0`, min: `0`, max: `0xffffffffffffffff`)
- **Outputs:** `CMF_OPTIONS` (dict)
- **Category:** `Cortiq/CMF`

### 3. `CMFTextGenerate`
- **Inputs:**
  - `model` (`CMF_MODEL`)
  - `prompt` (STRING, multiline)
  - `max_tokens` (INT, default: `256`, min: `1`, max: `8192`)
  - `options` (`CMF_OPTIONS`, optional)
- **Outputs:** `STRING` (generated text)
- **Category:** `Cortiq/CMF`

### 4. `CMFChatGenerate`
- **Inputs:**
  - `model` (`CMF_MODEL`)
  - `system_prompt` (STRING, multiline, default: `"You are a helpful assistant."`)
  - `user_prompt` (STRING, multiline)
  - `max_tokens` (INT, default: `256`, min: `1`, max: `8192`)
  - `options` (`CMF_OPTIONS`, optional)
- **Outputs:** `STRING` (assistant response)
- **Category:** `Cortiq/CMF`

---

## 5. Error Recovery Matrix

| Trigger / Condition | Direct Cause | System Recovery Behavior |
| :--- | :--- | :--- |
| `cortiq_ffi` dynamic library missing | Missing `.dll`/`.so`/`.dylib` in `bin/` | `FileNotFoundError` raised with build & installation instructions. |
| Non-existent or corrupted `.cmf` model | `cortiq_load` returns NULL | `cortiq_last_error()` queried; `RuntimeError` raised with Rust error message. |
| User clicks "Cancel" in ComfyUI | Processing interrupt signal | `cortiq_cancel(handle)` invoked asynchronously; node terminates cleanly without crashing Python. |
| Invalid JSON options payload | Malformed JSON in `cortiq_set_options` | Returns -1; `RuntimeError` raised with error payload string. |
| System out of RAM/VRAM | Allocation failure in Rust core | `cortiq_last_error()` catches OOM error and raises `MemoryError`. |
