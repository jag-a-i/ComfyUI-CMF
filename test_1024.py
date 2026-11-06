import sys
import os
import time

sys.path.insert(0, r"P:\Downloaded\ComfyUI_windows_portable\ComfyUI\custom_nodes\Comfy-CMF")
from wrapper import CMFWrapper

def main():
    model_path = r"P:\Downloaded\ComfyUI_windows_portable\ComfyUI\models\cmf\lumina-q4tp.cmf"
    w = CMFWrapper()
    w.set_gpu(True)
    print("Cooperative Matrix Active:", w.lib.cortiq_coop_matrix_active())

    def progress(step, total):
        print(f"Step {step}/{total} ({step/total*100:.1f}%)")

    t0 = time.time()
    img = w.generate_image(
        model_path=model_path,
        prompt="a beautiful photo of a cozy cabin in the snow",
        width=1024,
        height=1024,
        steps=20,
        guidance=3.5,
        seed=42,
        enable_gpu=True,
        num_threads=0,
        progress_callback=progress
    )
    t1 = time.time()
    print(f"1024x1024 finished in {t1 - t0:.2f}s! Shape: {img.shape}")

if __name__ == "__main__":
    main()
