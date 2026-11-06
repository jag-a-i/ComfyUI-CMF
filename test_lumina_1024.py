import sys
import time
import os
from pathlib import Path

# Add Comfy-CMF to sys.path
cmf_dir = Path(r"P:\Downloaded\ComfyUI_windows_portable\ComfyUI\custom_nodes\Comfy-CMF")
sys.path.insert(0, str(cmf_dir))

from wrapper import CMFWrapper

model_path = r"P:\Downloaded\ComfyUI_windows_portable\ComfyUI\models\cmf\lumina-q4tp.cmf"
print(f"Loading wrapper from {cmf_dir}...")
w = CMFWrapper()

def progress(step, total):
    print(f"  Step {step}/{total} ({(step/total)*100:.1f}%)")
    return True

print("Running 1024x1024 image generation (20 steps)...")
t0 = time.time()
img = w.generate_image(
    model_path=model_path,
    prompt="a photorealistic red sports car driving through neon city streets at night, 8k",
    width=1024,
    height=1024,
    steps=20,
    guidance=4.0,
    seed=42,
    enable_gpu=True,
    progress_callback=progress
)
dt = time.time() - t0
print(f"\n==========================================")
print(f"1024x1024 20-step generation finished in {dt:.2f}s!")
print(f"==========================================\n")

if hasattr(img, "save"):
    img.save("lumina_1024_result.png")
    print("Saved image to lumina_1024_result.png")
elif hasattr(img, "cpu"): # torch tensor
    from PIL import Image
    import numpy as np
    arr = (img.squeeze().cpu().numpy() * 255).clip(0, 255).astype(np.uint8)
    Image.fromarray(arr).save("lumina_1024_result.png")
    print("Saved image to lumina_1024_result.png")

