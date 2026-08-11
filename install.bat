@echo off
setlocal
echo [ComfyUI-CMF] Starting automated GPU binary installation...

python install.py %*
if %ERRORLEVEL% NEQ 0 (
    echo [ComfyUI-CMF] Installation failed. Please ensure Rust (cargo) is installed.
    exit /b %ERRORLEVEL%
)

echo [ComfyUI-CMF] Installation complete!
pause
