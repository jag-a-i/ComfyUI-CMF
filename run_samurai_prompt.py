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
artifact_dir = Path(r"C:\Users\blibd\.gemini\antigravity\brain\f299f14c-c00b-4863-ac78-e501f2f71004")

prompt = (
    "A breathtaking cinematic portrait of a gorgeous, seductive female samurai with intense dark eyes, "
    "holding a lit cigarette with delicate fingers, soft wisps of blue-grey smoke curling upward past her face. "
    "Traditional ornate black and crimson lacquered armor with gold dragon accents, slightly loosened at the collar, "
    "katana at her hip. Moody atmospheric neon lighting, soft rim light highlighting her cheekbones and dark hair, "
    "rain-slicked Edo street blending into misty neon reflections, photorealistic 8k, highly detailed, masterwork."
)

print("=" * 70)
print("SAMURAI LADY PROMPT GENERATION (1024x1024, 20 Steps)")
print(f"Prompt: {prompt}")
print("=" * 70)

w = CMFWrapper()
w.set_gpu(True)

def progress_cb(step, total):
    print(f"  [DiT Step {step:2d}/{total:2d}] ({(step/total)*100:5.1f}%)")
    return True

t0 = time.time()
img_tensor = w.generate_image(
    model_path=model_path,
    prompt=prompt,
    width=1024,
    height=1024,
    steps=20,
    guidance=4.0,
    seed=1337,
    enable_gpu=True,
    progress_callback=progress_cb
)
total_time = time.time() - t0

print("\n" + "=" * 70)
print(f"Generation Complete in {total_time:.2f}s!")
print("=" * 70)

arr = (img_tensor.squeeze().cpu().numpy() * 255.0).clip(0, 255).astype(np.uint8)
pil_img = Image.fromarray(arr)

out_local = cmf_dir / "samurai_lady_smoking_1024.png"
out_artifact = artifact_dir / "samurai_lady_smoking_1024.png"

pil_img.save(str(out_local))
print(f"Saved local image: {out_local}")

artifact_dir.mkdir(parents=True, exist_ok=True)
pil_img.save(str(out_artifact))
print(f"Saved artifact image: {out_artifact}")
