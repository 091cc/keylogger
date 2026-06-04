@echo off
title Keylogger Dependencies Installer

echo [1/3] Installing required Python packages...
py -m pip install pynput pywin32

echo [2/3] Running pywin32 post-install configuration...
py -m pywin32_postinstall -install

echo [3/4]Installing required Python packages...
py -m pip install pyautogui

echo [4/4]Installing required Python packages...
py -m pip install --upgrade Pillow

echo.
echo ==========================================
echo Installation completed successfully!
echo ==========================================
echo.
pause
