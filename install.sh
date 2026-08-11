#!/usr/bin/env bash
set -e

echo "[ComfyUI-CMF] Starting automated GPU binary installation..."

PYTHON_BIN="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_BIN="python"
fi

$PYTHON_BIN install.py "$@"
echo "[ComfyUI-CMF] Installation complete!"
