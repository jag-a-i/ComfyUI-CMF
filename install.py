#!/usr/bin/env python3
"""
ComfyUI-CMF Automated Build & Installation Script
Automatically builds native cortiq_ffi dynamic library with GPU acceleration.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).parent.resolve()
BIN_DIR = ROOT_DIR / "bin"
CMF_SOURCE_DIR = ROOT_DIR.parent / "cmf_source"
if not CMF_SOURCE_DIR.exists():
    CMF_SOURCE_DIR = ROOT_DIR / "cmf_source"


def get_lib_name() -> str:
    if sys.platform == "win32":
        return "cortiq_ffi.dll"
    elif sys.platform == "darwin":
        return "libcortiq_ffi.dylib"
    else:
        return "libcortiq_ffi.so"


def check_cargo() -> bool:
    try:
        res = subprocess.run(["cargo", "--version"], capture_output=True, text=True)
        return res.returncode == 0
    except FileNotFoundError:
        return False


def build_cortiq_ffi(force: bool = False) -> bool:
    lib_name = get_lib_name()
    target_bin = BIN_DIR / lib_name
    BIN_DIR.mkdir(parents=True, exist_ok=True)

    if target_bin.exists() and not force:
        print(f"[ComfyUI-CMF] Found pre-existing dynamic library: {target_bin}")
        return True

    print("[ComfyUI-CMF] Dynamic library missing or build forced. Initializing automatic GPU build...")

    if not check_cargo():
        print("[ComfyUI-CMF] ERROR: Rust compiler ('cargo') is not installed on system PATH.")
        print("[ComfyUI-CMF] Please install Rust from https://rustup.rs/ to compile native CMF GPU binaries.")
        return False

    if not CMF_SOURCE_DIR.exists():
        print(f"[ComfyUI-CMF] ERROR: Source directory not found at '{CMF_SOURCE_DIR}'.")
        return False

    print(f"[ComfyUI-CMF] Building cortiq-ffi with GPU features from '{CMF_SOURCE_DIR}'...")
    cmd = ["cargo", "build", "-p", "cortiq-ffi", "--release", "--features", "gpu"]

    try:
        subprocess.run(cmd, cwd=str(CMF_SOURCE_DIR), check=True)
        release_bin = CMF_SOURCE_DIR / "target" / "release" / lib_name
        if release_bin.exists():
            shutil.copy2(release_bin, target_bin)
            print(f"[ComfyUI-CMF] BUILD SUCCESS! Dynamic library installed to '{target_bin}'.")
            return True
        else:
            print(f"[ComfyUI-CMF] ERROR: Build output missing at '{release_bin}'.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"[ComfyUI-CMF] ERROR: Cargo build failed with exit code {e.returncode}.")
        return False


if __name__ == "__main__":
    force_build = "--force" in sys.argv
    success = build_cortiq_ffi(force=force_build)
    sys.exit(0 if success else 1)
