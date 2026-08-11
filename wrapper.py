import ctypes
import os
import sys
import json
from pathlib import Path
import numpy as np
import torch


class CMFWrapper:
    """
    Python ctypes wrapper for the CMF (Cortiq Model Format) Rust FFI library (cortiq-ffi).
    Manages loading the native dynamic library, defining C ABI signatures, GPU toggles, and error inspection.
    """
    
    def __init__(self, lib_path=None):
        if lib_path is None:
            lib_path = self._find_library()
            
        if not os.path.exists(lib_path):
            raise FileNotFoundError(
                f"[ComfyUI-CMF] Shared library not found at: '{lib_path}'. "
                "Please place cortiq_ffi.dll (Windows), libcortiq_ffi.so (Linux), or "
                "libcortiq_ffi.dylib (macOS) in the 'bin/' directory, or build using "
                "'cargo build -p cortiq-ffi --release'."
            )
            
        try:
            self.lib = ctypes.CDLL(lib_path)
        except Exception as e:
            raise RuntimeError(f"[ComfyUI-CMF] Failed to load dynamic library '{lib_path}': {e}")
            
        self._bind_signatures()

    def _find_library(self) -> str:
        """Dynamically detect host OS and locate cortiq_ffi dynamic library."""
        base_dir = Path(__file__).parent / "bin"
        
        if sys.platform == "win32":
            lib_name = "cortiq_ffi.dll"
        elif sys.platform == "darwin":
            lib_name = "libcortiq_ffi.dylib"
        else:
            lib_name = "libcortiq_ffi.so"

        # Check compiled GPU release target in cmf_source first
        build_target = Path(__file__).parent.parent.parent / "cmf_source" / "target" / "release" / lib_name
        if build_target.exists():
            return str(build_target)
            
        base_dir = Path(__file__).parent / "bin"
        target = base_dir / lib_name
        if target.exists():
            return str(target)
            
        alt_target = Path(__file__).parent / lib_name
        if alt_target.exists():
            return str(alt_target)

            
        return str(target)

    def _bind_signatures(self):
        """Bind C ABI function signatures matching cortiq.h."""
        # void *cortiq_load(const char *path);
        self.lib.cortiq_load.restype = ctypes.c_void_p
        self.lib.cortiq_load.argtypes = [ctypes.c_char_p]
        
        # void cortiq_set_gpu(bool enable);
        if hasattr(self.lib, "cortiq_set_gpu"):
            self.lib.cortiq_set_gpu.restype = None
            self.lib.cortiq_set_gpu.argtypes = [ctypes.c_bool]
            
        # void cortiq_set_threads(int32_t n);
        if hasattr(self.lib, "cortiq_set_threads"):
            self.lib.cortiq_set_threads.restype = None
            self.lib.cortiq_set_threads.argtypes = [ctypes.c_int32]
            
        # int32_t cortiq_set_options(void *handle, const char *json_options);
        self.lib.cortiq_set_options.restype = ctypes.c_int32
        self.lib.cortiq_set_options.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        
        # typedef bool (*cortiq_token_cb)(const char *token, void *user);
        self.CALLBACK_TYPE = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_char_p, ctypes.c_void_p)
        
        # int32_t cortiq_chat(void *handle, const char *prompt, uint32_t max_tokens, cortiq_token_cb cb, void *user);
        self.lib.cortiq_chat.restype = ctypes.c_int32
        self.lib.cortiq_chat.argtypes = [
            ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32, 
            self.CALLBACK_TYPE, ctypes.c_void_p
        ]

        # int32_t cortiq_chat_messages(void *handle, const char *json_messages, uint32_t max_tokens, cortiq_token_cb cb, void *user);
        if hasattr(self.lib, "cortiq_chat_messages"):
            self.lib.cortiq_chat_messages.restype = ctypes.c_int32
            self.lib.cortiq_chat_messages.argtypes = [
                ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32, 
                self.CALLBACK_TYPE, ctypes.c_void_p
            ]
        
        # typedef bool (*cortiq_progress_cb)(uint32_t step, uint32_t total_steps, void *user);
        self.PROGRESS_CALLBACK_TYPE = ctypes.CFUNCTYPE(
            ctypes.c_bool, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p
        )

        # int32_t cortiq_imagine(
        #     const char *model_path, const char *prompt,
        #     uint32_t width, uint32_t height, uint32_t steps,
        #     float guidance, uint64_t seed, uint8_t *out_rgb,
        #     cortiq_progress_cb progress, void *user
        # );
        if hasattr(self.lib, "cortiq_imagine"):
            self.lib.cortiq_imagine.restype = ctypes.c_int32
            self.lib.cortiq_imagine.argtypes = [
                ctypes.c_char_p,
                ctypes.c_char_p,
                ctypes.c_uint32,
                ctypes.c_uint32,
                ctypes.c_uint32,
                ctypes.c_float,
                ctypes.c_uint64,
                ctypes.POINTER(ctypes.c_uint8),
                self.PROGRESS_CALLBACK_TYPE,
                ctypes.c_void_p,
            ]

        
        # void cortiq_cancel(void *handle);
        if hasattr(self.lib, "cortiq_cancel"):
            self.lib.cortiq_cancel.restype = None
            self.lib.cortiq_cancel.argtypes = [ctypes.c_void_p]
            
        # const char *cortiq_last_error(void);
        if hasattr(self.lib, "cortiq_last_error"):
            self.lib.cortiq_last_error.restype = ctypes.c_char_p
            self.lib.cortiq_last_error.argtypes = []

        # const char *cortiq_execution_info(void);
        if hasattr(self.lib, "cortiq_execution_info"):
            self.lib.cortiq_execution_info.restype = ctypes.c_char_p
            self.lib.cortiq_execution_info.argtypes = []

        # void cortiq_free(void *handle);
        self.lib.cortiq_free.restype = None
        self.lib.cortiq_free.argtypes = [ctypes.c_void_p]

    def set_gpu(self, enable: bool = True):
        """Enable or disable discrete GPU graph acceleration (Vulkan / Metal). Must be called before load."""
        if hasattr(self.lib, "cortiq_set_gpu"):
            self.lib.cortiq_set_gpu(enable)

    def set_threads(self, num_threads: int = 0):
        """Set execution thread pool count (0 = automatic based on physical CPU cores)."""
        if hasattr(self.lib, "cortiq_set_threads"):
            self.lib.cortiq_set_threads(num_threads)

    def get_last_error(self) -> str:
        """Extract thread-local diagnostic error string from C runtime."""
        if hasattr(self.lib, "cortiq_last_error"):
            err_ptr = self.lib.cortiq_last_error()
            if err_ptr:
                return ctypes.string_at(err_ptr).decode("utf-8", errors="replace")
        return "Unknown CMF FFI error"

    def get_execution_info(self) -> str:
        """Query execution environment info JSON."""
        if hasattr(self.lib, "cortiq_execution_info"):
            info_ptr = self.lib.cortiq_execution_info()
            if info_ptr:
                return ctypes.string_at(info_ptr).decode("utf-8", errors="replace")
        return "{}"

    def load_model(self, model_path: str, enable_gpu: bool = True, num_threads: int = 0):
        """Memory-map and open a .cmf model file, returning a CMFModelHandle."""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"[ComfyUI-CMF] Model file not found: '{model_path}'")
            
        self.set_gpu(enable_gpu)
        self.set_threads(num_threads)
        
        handle = self.lib.cortiq_load(model_path.encode("utf-8"))
        if not handle:
            err = self.get_last_error()
            raise RuntimeError(f"[ComfyUI-CMF] Failed to load model '{model_path}': {err}")
            
        return CMFModelHandle(self, handle, model_path)

    def generate_image(
        self,
        model_path: str,
        prompt: str,
        width: int,
        height: int,
        steps: int,
        guidance: float,
        seed: int,
        enable_gpu: bool = True,
        num_threads: int = 0,
        interrupt_check_fn=None,
    ) -> torch.Tensor:
        """
        Generate an image using cortiq_imagine Rust FFI binding.
        Allocates uint8 RGB numpy array, populates via C-FFI, and returns float32 PyTorch tensor [1, H, W, 3] normalized in [0.0, 1.0].
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"[ComfyUI-CMF] Model file not found: '{model_path}'")

        if not hasattr(self.lib, "cortiq_imagine"):
            raise NotImplementedError("[ComfyUI-CMF] Current cortiq_ffi library build lacks cortiq_imagine support.")

        self.set_gpu(enable_gpu)
        self.set_threads(num_threads)

        rgb_np = np.zeros((height, width, 3), dtype=np.uint8)
        out_ptr = rgb_np.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))

        def py_progress_cb(step, total_steps, user_data):
            if interrupt_check_fn and interrupt_check_fn():
                return False
            return True

        c_progress_cb = self.PROGRESS_CALLBACK_TYPE(py_progress_cb)

        res = self.lib.cortiq_imagine(
            model_path.encode("utf-8"),
            prompt.encode("utf-8"),
            int(width),
            int(height),
            int(steps),
            float(guidance),
            int(seed),
            out_ptr,
            c_progress_cb,
            None,
        )

        if res < 0:
            err = self.get_last_error()
            raise RuntimeError(f"[ComfyUI-CMF] Image generation failed: {err}")

        image_tensor = torch.from_numpy(rgb_np).to(torch.float32) / 255.0
        return image_tensor.unsqueeze(0)



class CMFModelHandle:
    """
    RAII wrapper around CMF opaque void* model handles.
    Ensures memory-mapped files and C memory structures are freed via cortiq_free.
    """
    
    def __init__(self, wrapper: CMFWrapper, handle: int, path: str):
        self.wrapper = wrapper
        self.handle = handle
        self.path = path
        self._closed = False

    def set_options(self, options_dict: dict):
        """Serialize sampler options to JSON and pass to Rust runtime."""
        if self._closed or not self.handle:
            raise RuntimeError("[ComfyUI-CMF] Attempted to set options on closed model handle.")
            
        opt_json = json.dumps(options_dict).encode("utf-8")
        res = self.wrapper.lib.cortiq_set_options(self.handle, opt_json)
        if res != 0:
            err = self.wrapper.get_last_error()
            raise RuntimeError(f"[ComfyUI-CMF] Failed to set options: {err}")

    def generate(self, prompt: str, max_tokens: int, interrupt_check_fn=None) -> str:
        """
        Execute single-turn streaming prompt generation.
        Checks interrupt_check_fn periodically and invokes cortiq_cancel if requested.
        """
        if self._closed or not self.handle:
            raise RuntimeError("[ComfyUI-CMF] Attempted generation on closed model handle.")
            
        output_tokens = []
        
        def py_callback(token_ptr, user_data):
            if interrupt_check_fn and interrupt_check_fn():
                if hasattr(self.wrapper.lib, "cortiq_cancel"):
                    self.wrapper.lib.cortiq_cancel(self.handle)
                return False
                
            if token_ptr:
                token_str = ctypes.string_at(token_ptr).decode("utf-8", errors="replace")
                output_tokens.append(token_str)
            return True

        c_callback = self.wrapper.CALLBACK_TYPE(py_callback)
        
        res = self.wrapper.lib.cortiq_chat(
            self.handle, prompt.encode("utf-8"), max_tokens, c_callback, None
        )
        
        if res < 0:
            err = self.wrapper.get_last_error()
            raise RuntimeError(f"[ComfyUI-CMF] Text generation failed: {err}")
            
        return "".join(output_tokens)

    def generate_messages(self, messages_list: list, max_tokens: int, interrupt_check_fn=None) -> str:
        """Execute multi-turn chat template generation using cortiq_chat_messages."""
        if self._closed or not self.handle:
            raise RuntimeError("[ComfyUI-CMF] Attempted generation on closed model handle.")
            
        if not hasattr(self.wrapper.lib, "cortiq_chat_messages"):
            raise NotImplementedError("[ComfyUI-CMF] Current cortiq_ffi library build lacks cortiq_chat_messages support.")
            
        output_tokens = []
        
        def py_callback(token_ptr, user_data):
            if interrupt_check_fn and interrupt_check_fn():
                if hasattr(self.wrapper.lib, "cortiq_cancel"):
                    self.wrapper.lib.cortiq_cancel(self.handle)
                return False
                
            if token_ptr:
                token_str = ctypes.string_at(token_ptr).decode("utf-8", errors="replace")
                output_tokens.append(token_str)
            return True

        c_callback = self.wrapper.CALLBACK_TYPE(py_callback)
        msgs_json = json.dumps(messages_list).encode("utf-8")
        
        res = self.wrapper.lib.cortiq_chat_messages(
            self.handle, msgs_json, max_tokens, c_callback, None
        )
        
        if res < 0:
            err = self.wrapper.get_last_error()
            raise RuntimeError(f"[ComfyUI-CMF] Chat messages generation failed: {err}")
            
        return "".join(output_tokens)

    def close(self):
        """Explicitly release Rust model handle and unmap memory."""
        if not self._closed and self.handle:
            self.wrapper.lib.cortiq_free(self.handle)
            self.handle = None
            self._closed = True

    def __del__(self):
        self.close()
