import os
import sys
from pathlib import Path

# Automatically build dynamic library if missing on node load
try:
    from .install import build_cortiq_ffi
    build_cortiq_ffi()
except Exception as e:
    print(f"[ComfyUI-CMF] Automatic GPU build check skipped: {e}")

import folder_paths
from .nodes import (
    CMFModelLoader,
    CMFSamplerOptions,
    CMFTextGenerate,
    CMFChatGenerate,
    CMFImageGenerate,
)


# Register custom model folder path for ComfyUI
cmf_model_path = os.path.join(folder_paths.models_dir, "cmf")
if not os.path.exists(cmf_model_path):
    try:
        os.makedirs(cmf_model_path, exist_ok=True)
    except Exception:
        pass

folder_paths.add_model_folder_path("cmf", cmf_model_path)

NODE_CLASS_MAPPINGS = {
    "CMFModelLoader": CMFModelLoader,
    "CMFSamplerOptions": CMFSamplerOptions,
    "CMFTextGenerate": CMFTextGenerate,
    "CMFChatGenerate": CMFChatGenerate,
    "CMFImageGenerate": CMFImageGenerate,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CMFModelLoader": "Load CMF Model",
    "CMFSamplerOptions": "CMF Sampler Options",
    "CMFTextGenerate": "CMF Text Generation",
    "CMFChatGenerate": "CMF Chat Generation",
    "CMFImageGenerate": "CMF Image Generation",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
