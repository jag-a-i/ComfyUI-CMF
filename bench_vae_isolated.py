import sys
import time
import os
from pathlib import Path
import numpy as np

cmf_dir = Path(r"P:\Downloaded\ComfyUI_windows_portable\ComfyUI\custom_nodes\Comfy-CMF")
sys.path.insert(0, str(cmf_dir))

from wrapper import CMFWrapper

model_path = r"P:\Downloaded\ComfyUI_windows_portable\ComfyUI\models\cmf\lumina-q4tp.cmf"
w = CMFWrapper()
w.set_gpu(True)

# Generate 1 step to get latents and measure pure VAE decode time cleanly
os.environ["CMF_GPU"] = "1"
os.environ["CMF_VAE_GPU_RESNET"] = "1"
os.environ["CMF_VAE_PROF"] = "1"

print("=" * 60)
print("RUNNING ISOLATED VAE DECODE BENCHMARK (1024x1024)")
print("=" * 60)

for iteration in range(1, 3):
    print(f"\n--- Iteration {iteration} ---")
    t0 = time.time()
    img = w.generate_image(
        model_path=model_path,
        prompt="A photo of a cat",
        width=1024,
        height=1024,
        steps=1,
        guidance=1.0,
        seed=42,
        enable_gpu=True,
    )
    total_time = time.time() - t0
    print(f"Total time iteration {iteration}: {total_time:.2f}s")
