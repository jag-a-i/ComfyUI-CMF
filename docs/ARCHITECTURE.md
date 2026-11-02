# Architecture Specifications: ComfyUI-CMF

- **Component:** `ComfyUI-CMF` (Cortiq Model Format Custom Nodes for ComfyUI)
- **Version:** 1.1.0
- **Target Environment:** Python 3.10+ / PyTorch / ComfyUI / Rust C-FFI (`cortiq-ffi`)

---

## 1. System Context & Overview

`ComfyUI-CMF` integrates the **Cortiq Model Format (CMF)** Rust inference engine into ComfyUI. CMF provides high-performance, low-memory-footprint execution of 4-bit quantized Language Models, Vision-Language Models, and Diffusion Transformers (`Lumina-Image 2.0`) using native memory mapping (`mmap`) and Vulkan/wgpu GPU acceleration.

```
+-----------------------------------------------------------------------+
|                            ComfyUI Engine                             |
+-----------------------------------------------------------------------+
                                   |
        +--------------------------+--------------------------+
        |                          |                          |
        v                          v                          v
+---------------+          +---------------+          +------------------+
|CMFModelLoader |          |CMFSamplerOpts |          | CMFImageGenerate |
+-------+-------+          +-------+-------+          +--------+---------+
        |                          |                           |
        | (CMFModelHandle)         | (Options Dict)            | (IMAGE Tensor)
        +-------------+------------+                           |
                      |                                        |
                      v                                        |
        +---------------------------+                          |
        | CMFTextGenerate / CMFChat |                          |
        +-------------+-------------+                          |
                      |                                        |
                      +-------------------+--------------------+
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
/* Engine version, static UTF-8. */
const char *cortiq_version(void);

/* Open a .cmf file (memory-mapped). Returns opaque handle pointer; NULL on error. */
void *cortiq_load(const char *path);

/* Globally enable or disable discrete GPU graph. Must be called before cortiq_load. */
void cortiq_set_gpu(bool enable);

/* True when this build has a working GPU backend and adapter. */
bool cortiq_gpu_available(void);

/* True when Tensor Core cooperative matrices are active on the GPU. */
bool cortiq_coop_matrix_active(void);

/* Set thread count for multi-threaded inference pool. 0 = auto. */
void cortiq_set_threads(int32_t n);

/* Set runtime JSON options (temperature, top_p, top_k, repetition_penalty, greedy, seed). Returns 0 on success, -1 on error. */
int32_t cortiq_set_options(void *handle, const char *json_options);

/* Single turn streaming chat generation. Returns total tokens generated or -1 on error. */
int32_t cortiq_chat(void *handle, const char *prompt, uint32_t max_tokens, cortiq_token_cb cb, void *user);

/* Raw completion without chat template wrapping. */
int32_t cortiq_complete(void *handle, const char *prompt, uint32_t max_tokens, cortiq_token_cb cb, void *user);

/* Multi-turn structured JSON message list generation. Returns total tokens or -1 on error. */
int32_t cortiq_chat_messages(void *handle, const char *json_messages, uint32_t max_tokens, cortiq_token_cb cb, void *user);

/* Text -> image (Lumina-Image 2.0 packed .cmf). Writes height*width*3 interleaved RGB8 bytes into out_rgb. */
int32_t cortiq_imagine(const char *model_path, const char *prompt, uint32_t width, uint32_t height,
                       uint32_t steps, float guidance, uint64_t seed, uint8_t *out_rgb,
                       cortiq_progress_cb progress, void *user);

/* Decode VAE latents [16, h_in, w_in] into planar RGB float [3, 8*h_in, 8*w_in]. */
int32_t cortiq_vae_decode(const char *model_path, const float *latents, uint32_t h_in, uint32_t w_in, float *out_rgb);

/* Asynchronously cancel generation running on handle (thread-safe). */
void cortiq_cancel(void *handle);

/* Get thread-local error message from previous failed FFI call. */
const char *cortiq_last_error(void);

/* Get JSON execution environment status {"simd": "avx2", "threads": 4, "gpu_backend": true}. */
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

1. During text (`cortiq_chat`, `cortiq_chat_messages`) or image (`cortiq_imagine`) generation, Python registers a `CFUNCTYPE` callback held in local scope for the duration of the FFI call.
2. Inside the callback, `comfy.model_management.processing_interrupted()` is checked on every token or denoising step.
3. If interrupted, the callback signals Rust to stop immediately (`cortiq_cancel(handle)` / returning `False`).
4. Upon return from the C FFI call, the node invokes `comfy.model_management.throw_exception_if_processing_interrupted()` so ComfyUI cleanly halts the workflow queue without raising a false `RuntimeError` modal.

---

## 4. ComfyUI Node Specifications

### 1. `CMFModelLoader`
- **Inputs:** `model_name` (dropdown of `.cmf` files in `models/cmf/`), `enable_gpu` (BOOLEAN), `threads` (INT)
- **Outputs:** `CMF_MODEL` (`CMFModelHandle`)
- **Category:** `Cortiq/CMF`

### 2. `CMFSamplerOptions`
- **Inputs:** `temperature`, `top_p`, `top_k`, `repetition_penalty`, `greedy`, `seed`
- **Outputs:** `CMF_OPTIONS` (dict)
- **Category:** `Cortiq/CMF`

### 3. `CMFTextGenerate`
- **Inputs:** `model` (`CMF_MODEL`), `prompt` (STRING, multiline), `max_tokens` (INT), `options` (`CMF_OPTIONS`, optional; resets to `DEFAULT_SAMPLER_OPTIONS` when disconnected)
- **Outputs:** `STRING` (generated text)
- **Category:** `Cortiq/CMF`

### 4. `CMFChatGenerate`
- **Inputs:** `model` (`CMF_MODEL`), `system_prompt` (STRING), `user_prompt` (STRING), `max_tokens` (INT), `options` (`CMF_OPTIONS`, optional; resets to `DEFAULT_SAMPLER_OPTIONS` when disconnected)
- **Outputs:** `STRING` (assistant response)
- **Category:** `Cortiq/CMF`

### 5. `CMFImageGenerate`
- **Inputs:** `model_name` (`.cmf` file), `prompt` (STRING), `width` (INT), `height` (INT), `steps` (INT), `guidance` (FLOAT), `seed` (INT), `enable_gpu` (BOOLEAN), `threads` (INT)
- **Outputs:** `IMAGE` (`torch.Tensor` of shape `[1, H, W, 3]`, `float32` normalized in `[0.0, 1.0]`)
- **Category:** `Cortiq/CMF`
