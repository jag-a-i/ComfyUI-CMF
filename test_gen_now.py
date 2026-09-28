import sys
import time
import os
from pathlib import Path
from PIL import Image
import numpy as np

cmf_dir = Path(r"P:\Downloaded\ComfyUI_windows_portable\ComfyUI\custom_nodes\Comfy-CMF")
sys.path.insert(0, str(cmf_dir))

from wrapper import CMFWrapper

model_path = r"P:\Downloaded\ComfyUI_windows_portable\ComfyUI\models\cmf\lumina-q4tp.cmf"
w = CMFWrapper()
w.set_gpu(True)

os.environ["CMF_GPU"] = "1"
os.environ["CMF_VAE_GPU_RESNET"] = "1"
os.environ["CMF_VAE_PROF"] = "1"
os.environ["CMF_CFG_TRUNC"] = "0.75"

prompt = "A stunning Japanese female samurai in an ornate black and gold embroidered silk kimono, elegantly holding and smoking a slender kiseru pipe, delicate wisps of smoke curling in the air, traditional katana on her hip, fierce sensual gaze, soft volumetric moonlit atmosphere with floating cherry blossom petals, masterwork photorealistic 8k portrait"

output_path = r"C:\Users\blibd\.gemini\antigravity\brain\f299f14c-c00b-4863-ac78-e501f2f71004\samurai_lady_now_1024.png"

print("=" * 60)
print("STARTING LUMINA 1024x1024 GENERATION TEST")
print("=" * 60)

t0 = time.time()
img_tensor = w.generate_image(
    model_path=model_path,
    prompt=prompt,
    width=1024,
    height=1024,
    steps=14,
    guidance=4.0,
    seed=42,
    enable_gpu=True,
)
total_time = time.time() - t0

# img_tensor is torch.Tensor [1, H, W, 3] or [1, 3, H, W]
arr = img_tensor.squeeze(0).cpu().numpy()
if arr.shape[0] == 3 and arr.ndim == 3:
    arr = np.transpose(arr, (1, 2, 0))
arr = (np.clip(arr, 0.0, 1.0) * 255.0).astype(np.uint8)
img = Image.fromarray(arr)
img.save(output_path)

print(f"\n============================================================")
print(f"GENERATION COMPLETE IN {total_time:.2f}s!")
print(f"Saved image to: {output_path}")
print(f"============================================================")
