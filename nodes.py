import os
import sys
import folder_paths
import comfy.model_management
from .wrapper import CMFWrapper, CMFModelHandle

# Global wrapper singleton
_wrapper_instance = None

def get_cmf_wrapper():
    """Lazy initialize global CMFWrapper singleton."""
    global _wrapper_instance
    if _wrapper_instance is None:
        _wrapper_instance = CMFWrapper()
    return _wrapper_instance


class CMFModelLoader:
    """
    ComfyUI Node to select and load Cortiq Model Format (.cmf) files.
    Discovers files in ComfyUI/models/cmf/ directory.
    Exposes GPU acceleration and thread pool controls.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        # Retrieve list of available .cmf models from folder_paths
        cmf_models = folder_paths.get_filename_list("cmf")
        if not cmf_models:
            # Fallback check
            cmf_dir = os.path.join(folder_paths.models_dir, "cmf")
            if os.path.exists(cmf_dir):
                cmf_models = [f for f in os.listdir(cmf_dir) if f.endswith(".cmf")]
            if not cmf_models:
                cmf_models = ["none_found"]
                
        return {
            "required": {
                "model_name": (cmf_models,),
                "enable_gpu": ("BOOLEAN", {"default": True}),
                "threads": ("INT", {"default": 0, "min": 0, "max": 64, "step": 1}),
            }
        }

    RETURN_TYPES = ("CMF_MODEL",)
    RETURN_NAMES = ("model",)
    FUNCTION = "load"
    CATEGORY = "Cortiq/CMF"

    def load(self, model_name, enable_gpu=True, threads=0):
        if model_name == "none_found":
            raise RuntimeError(
                "[ComfyUI-CMF] No .cmf files found in 'ComfyUI/models/cmf/'. "
                "Please place your CMF quantized model files in that directory."
            )
            
        wrapper = get_cmf_wrapper()
        full_path = folder_paths.get_full_path("cmf", model_name)
        if not full_path:
            full_path = os.path.join(folder_paths.models_dir, "cmf", model_name)
            
        handle = wrapper.load_model(full_path, enable_gpu=enable_gpu, num_threads=threads)
        return (handle,)


class CMFSamplerOptions:
    """
    ComfyUI Node to configure text generation sampling parameters
    (temperature, top_p, top_k, repetition penalty, greedy, seed).
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.01}),
                "top_p": ("FLOAT", {"default": 0.9, "min": 0.0, "max": 1.0, "step": 0.01}),
                "top_k": ("INT", {"default": 40, "min": 0, "max": 200, "step": 1}),
                "repetition_penalty": ("FLOAT", {"default": 1.1, "min": 1.0, "max": 2.0, "step": 0.01}),
                "greedy": ("BOOLEAN", {"default": False}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            }
        }

    RETURN_TYPES = ("CMF_OPTIONS",)
    RETURN_NAMES = ("options",)
    FUNCTION = "configure"
    CATEGORY = "Cortiq/CMF"

    def configure(self, temperature, top_p, top_k, repetition_penalty, greedy, seed):
        options = {
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "repetition_penalty": repetition_penalty,
            "greedy": greedy,
            "seed": seed,
        }
        return (options,)


class CMFTextGenerate:
    """
    ComfyUI Node for single-turn prompt text generation.
    Supports periodic ComfyUI processing interruption checks.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("CMF_MODEL",),
                "prompt": ("STRING", {"multiline": True, "default": "Write a short poem about artificial intelligence."}),
                "max_tokens": ("INT", {"default": 256, "min": 1, "max": 8192, "step": 1}),
            },
            "optional": {
                "options": ("CMF_OPTIONS",),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "generate"
    CATEGORY = "Cortiq/CMF"

    def generate(self, model: CMFModelHandle, prompt: str, max_tokens: int, options: dict = None):
        if not isinstance(model, CMFModelHandle):
            raise TypeError(f"[ComfyUI-CMF] Invalid model type received: {type(model)}")
            
        if options:
            model.set_options(options)

        def interrupt_check():
            return comfy.model_management.processing_interrupted()

        result = model.generate(prompt, max_tokens, interrupt_check_fn=interrupt_check)
        return (result,)


class CMFChatGenerate:
    """
    ComfyUI Node for multi-turn structured chat generation (System Prompt + User Prompt).
    Uses cortiq_chat_messages FFI call.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("CMF_MODEL",),
                "system_prompt": ("STRING", {"multiline": True, "default": "You are a helpful, creative AI assistant."}),
                "user_prompt": ("STRING", {"multiline": True, "default": "How does memory mapping improve model loading speed?"}),
                "max_tokens": ("INT", {"default": 256, "min": 1, "max": 8192, "step": 1}),
            },
            "optional": {
                "options": ("CMF_OPTIONS",),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("response",)
    FUNCTION = "generate_chat"
    CATEGORY = "Cortiq/CMF"

    def generate_chat(self, model: CMFModelHandle, system_prompt: str, user_prompt: str, max_tokens: int, options: dict = None):
        if not isinstance(model, CMFModelHandle):
            raise TypeError(f"[ComfyUI-CMF] Invalid model type received: {type(model)}")
            
        if options:
            model.set_options(options)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        def interrupt_check():
            return comfy.model_management.processing_interrupted()

        result = model.generate_messages(messages, max_tokens, interrupt_check_fn=interrupt_check)
        return (result,)
