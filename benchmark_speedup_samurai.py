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

w = CMFWrapper()
w.set_gpu(True)

def progress_cb(step, total):
    print(f"  [DiT Step {step:2d}/{total:2d}] ({(step/total)*100:5.1f}%)")
    return True

print("=" * 75)
print("BENCHMARK TEST: SAMURAI LADY 1024x1024 (EVALUATING CACHE & SCALED STEPS)")
print("=" * 75)

# Test Run: 14 Steps with Prompt Cache Verification
print("\n>>> Executing 14-Step Generation (Seed 1337)...")
t0 = time.time()
img_14 = w.generate_image(
    model_path=model_path,
    prompt=prompt,
    width=1024,
    height=1024,
    steps=14,
    guidance=4.0,
    seed=1337,
    enable_gpu=True,
    progress_callback=progress_cb
)
time_14 = time.time() - t0

out_14_local = cmf_dir / "samurai_lady_1024_14steps.png"
out_14_art = artifact_dir / "samurai_lady_1024_14steps.png"

arr_14 = (img_14.squeeze().cpu().numpy() * 255.0).clip(0, 255).astype(np.uint8)
pil_14 = Image.fromarray(arr_14)
pil_14.save(str(out_14_local))
pil_14.save(str(out_14_art))

print(f"\n14-Step Run Complete in {time_14:.2f}s! Saved to {out_14_art.name}")
print("=" * 75)
