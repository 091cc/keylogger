@echo off
title Keylogger Dependencies Installer

echo [1/2] Installing required Python packages...
python -m pip install pynput pywin32

echo [2/2] Running pywin32 post-install configuration...
python -m pywin32_postinstall -install

echo.
echo ==========================================
echo Installation completed successfully!
echo ==========================================
echo.
pause
