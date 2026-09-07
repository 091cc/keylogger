# KEYLOGGER

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

**A modern, research-grade Windows keylogger built on Python 3.8+**  
Unicode-aware · Clipboard monitoring · Dual-mode operation (Local / SMTP) · Configurable log path · Global hotkey (F9)

</div>

---

> [!WARNING]
> **LEGAL DISCLAIMER**  
> This software is provided **for educational and security research purposes only**.  
> Unauthorized use on systems you do not own or have explicit written permission to test is **illegal** and may result in criminal prosecution.  
> The author assumes **no liability** for any misuse or damage caused by this tool.  
> **Always obtain proper authorization before deployment.**

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Gmail App Password Setup](#gmail-app-password-setup)
- [Usage](#usage)
- [Global Hotkey (F9)](#global-hotkey-f9)
- [Log Path Configuration](#log-path-configuration)
- [Auto-Start on Windows Boot](#auto-start-on-windows-boot)
- [Log Format](#log-format)
- [Technical Notes](#technical-notes)
- [Reference](#reference)
- [License](#license)

---

## Overview

KEYLOGGER v3 is a modernized rewrite of the keylogger example from **[Black Hat Python, 2nd Edition](https://nostarch.com/black-hat-python2E)** (No Starch Press). It has been fully updated for Python 3 with significant architectural improvements:

- Migrated from the deprecated `pyWinhook` to the actively maintained `pynput` library
- Replaced ANSI Windows API calls with **Unicode (Wide) Win32 API** via `ctypes`, enabling proper support for multi-language window titles (e.g., Traditional Chinese, Japanese, Korean)
- Introduced dual-mode runtime configuration via GUI dialog — no hardcoded credentials
- Added **configurable log storage path** with persistent settings
- Implemented **global F9 hotkey** to hide/show the control window

---

## Features

| Feature | Description |
|---|---|
| ⌨️ **Real-time Keylogging** | Captures all keystrokes, including Numpad (0–9) and special/function keys with proper formatting `[SPACE]`, `[WIN]`, `[R_SHIFT]` etc. |
| 🪟 **Window Tracking** | Logs PID, executable name, and active window title on focus change (full Unicode support via `ctypes`) |
| 📋 **Clipboard Monitoring** | Automatically captures clipboard content on `Ctrl+V` |
| 🔀 **Dual Operation Modes** | Choose between **Local-Only** (file storage) or **SMTP** (auto email) at startup |
| 👻 **Background Mode** | `.pyw` extension enables silent execution with no console window |
| 📧 **Email Transmission** | Auto-delivers `log.txt` via SMTP every **10 minutes** |
| 🛡️ **Fail-Safe Logging** | Local log is only cleared after a **confirmed successful** email delivery |
| 🔒 **Encrypted Transit** | Uses `STARTTLS` (Port 587) — credentials and logs are always encrypted |
| 🔑 **Secure Credentials** | GUI-based App Password input — no secrets hardcoded in source |
| 📂 **Configurable Log Path** | Browse and select any storage location for `log.txt`; settings persist across sessions |
| ⌨️ **Global Hotkey (F9)** | Hide or show the control window at any time, even when minimized or out of focus |
| 🔄 **Real-time Path Update** | Change log path while logger is running — updates immediately |
| 💾 **Persistent Settings** | Log path and email configuration are saved locally and restored on next launch |

---

## Tech Stack

- **Primary Language**: Python
- **Operating System**: Windows
- **Core Libraries**: `pynput`, `pywin32`
- **GUI**: `tkinter` (built-in)

---

## Project Structure

```text
├── keylogger.pyw           # Core script: Includes GUI, auto-dep install, keystroke/clipboard logging, and email reports (F9 hotkey)
├── keylogger_config.json   # Auto-generated: Stores log paths and email settings (Do not commit to version control)
├── LICENSE                 # Project open-source license
└── README.md               # Project documentation
```


---

## Prerequisites

- **OS**: Windows (7 / 10 / 11)
- **Python**: 3.8+ recommended (developed and tested on 3.14; not compatible with Python 2 or 3.5 and below)
- **Core dependencies**: `pynput`, `pywin32` (auto-installed on first run)

### Python Version Compatibility

| Python Version | Status | Notes |
|---|---|---|
| 3.8 – 3.14 | ✅ Fully supported | Recommended range |
| 3.6 – 3.7 | ⚠️ Partial | May work, but requires pinning older `pynput` version |
| 3.5 and below | ❌ Not supported | f-string syntax causes `SyntaxError` |
| 2.x | ❌ Not supported | Incompatible entirely |

> [!NOTE]
> The code uses no Python 3.14-exclusive syntax and runs on any **Python 3.8+** installation. Dependencies are automatically installed on first execution.

---

## Installation

### Option 1 — One-Click Setup *(Recommended)*

Simply double-click `keylogger.pyw`. The program will:
1. Display a progress bar showing installation status
2. Auto-install all required dependencies (`pynput`, `pywin32`)
3. Auto-run `pywin32_postinstall`
4. Launch the configuration dialog

### Option 2 — Manual Setup

**Core keylogger:**

```batch
py -m pip install pynput pywin32
py -m pywin32_postinstall -install
```

---

## Gmail App Password Setup

To use the SMTP auto-email feature with Gmail:
1. Enable **2-Step Verification** on your Google Account → [myaccount.google.com/security](myaccount.google.com/security)
2. Navigate to **Security → App Passwords**
3. Generate a new **16-digit App Password** (select "Mail" and your device)
4. Use this password when the program prompts at startup

---

> [!TIP]
> Use a dedicated **"burner" Gmail account** for testing to isolate risk and keep your personal account clean.

---

## Usage

1. Double-click `keylogger.pyw` — a progress window appears (first run only)
2. A configuration dialog will appear:
   - **"Would you like to send logs via Email?"**
       - Select Yes → Enter sender email, 16-digit App Password, and receiver email
       - Select No → Logs are saved locally only (auto-reset disabled)
3. The main control window appears with:
    - Current status (Stopped / Running)
    - Log file path (configurable)
    - **Start Logger** / **Stop Logger** buttons
    - F9 hotkey indicator
4. Click **Start Logger** to begin recording
5. In SMTP mode, check your inbox every ~10 minutes for the `Keylogger Report`

**To terminate**: Click **Exit** on the control window, or press `Ctrl+Shift+Esc` → find `pythonw.exe` → End Task

---

## Global Hotkey (F9)

The control window can be hidden or shown at any time using the **F9** key:
| Action | Behavior |
| :--- | :--- |
| **Press F9** | **Toggles window visibility** (Hide / Show). |
| **When Hidden** | The program **continues running silently in the background**. |
| **When Shown** | Pressing **F9** again brings the window back to the foreground. |
| **Global** | Works universally, **even when the window is not in focus**. |

> [!TIP]
> Use F9 to keep the control window out of sight while the keylogger continues running.

---

## Log Path Configuration
The program allows you to customize where `log.txt` is saved:
| Feature | Description |
| :--- | :--- |
| **Browse Button** | **Click to select any folder and filename for your log. |
| **Default Location** | `Desktop\keylog.txt` (persists across sessions) |
| **Path Display** | Shows current log path in the control window |
| **Auto-save** | Settings are saved to `keylogger_config.json` |
| **Real-time Update** | Change path while logger is running — updates immediately |

### Why this matters:
- When running from a USB drive, you can save logs to the computer's hard drive
- Prevents log loss if the USB drive is removed
- Organize logs across multiple computers or projects
- No need to search for `log.txt` — set your preferred location

---

## Log Format
Each session log (`log.txt`) follows this structure:
```
[ PID: 1234 - notepad.exe - 無標題 - 記事本 ]
Hello world!
[ENTER]

[ PID: 5678 - chrome.exe - Google 搜尋 ]
How to use Python
[ENTER]

[PASTE] - https://github.com/091cc/keylogger

[ PID: 1234 - notepad.exe - 無標題 - 記事本 ]
[SPACE][BACKSPACE][TAB][WIN][R_SHIFT]
```
- **Header block**: PID · Executable name · Window title (full Unicode support)
- **Keystroke body**: Raw input including special keys in `[brackets]`
- **Special key formatting**: `[SPACE]`, `[WIN]`, `[R_SHIFT]`, `[CTRL]`, `[ALT]`, `[ENTER]`, `[BACKSPACE]`, `[TAB]`, `[ESC]`, `[UP]`, `[DOWN]`, `[LEFT]`, `[RIGHT]`, etc.
- **Clipboard entries**: Prefixed with `[PASTE]` on every `Ctrl+V` event

---

## Technical Notes
- **Unicode Support**: Uses `GetWindowTextW` and `GetForegroundWindow` via `ctypes` to correctly capture CJK and other non-ASCII window titles
- **Event Backend**: `pynput` replaces the unmaintained `pyWinhook`, providing better compatibility with modern Python versions
- **SMTP Security**: All email transmissions use `STARTTLS` on port 587 — plaintext transmission is never used
- **No Hardcoded Secrets**: Credentials are entered at runtime via GUI and never written to disk
- **Global Hotkey**: F9 uses `pynput` global listener — works even when the window is hidden or out of focus
- **Auto-install**: Dependencies are installed on first run with a progress bar, eliminating manual setup
- **Persistent Settings**: `keylogger_config.json` stores log path and settings for convenience
- **Real-time Log Path Update**: Changing the log path while the logger is running updates immediately — no restart required

---

##  Reference
- [Black Hat Python, 2nd Edition — No Starch Press](https://nostarch.com/black-hat-python2E)
- [pynput Documentation](https://pynput.readthedocs.io/)
- [pywin32 on PyPI](https://pypi.org/project/pywin32/)

---

## License
This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
