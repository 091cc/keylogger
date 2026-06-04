# KEYLOGGER v3

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

**A modern, research-grade Windows keylogger built on Python 3.14**  
Unicode-aware · Clipboard monitoring · Screenshot capture · Dual-mode operation (Local / SMTP)

</div>

---

> [!WARNING]
> **LEGAL DISCLAIMER**  
> This software is provided **for educational and security research purposes only**.  
> Unauthorized use on systems you do not own or have explicit written permission to test is **illegal** and may result in criminal prosecution.  
> The author assumes **no liability** for any misuse or damage caused by this tool.  
> **Always obtain proper authorization before deployment.**

---

## 📖 Overview

KEYLOGGER v3.14 is a modernized rewrite of the keylogger example from **[Black Hat Python, 2nd Edition](https://nostarch.com/black-hat-python2E)** (No Starch Press). It has been fully updated for Python 3.14 with significant architectural improvements:

- Migrated from the deprecated `pyWinhook` to the actively maintained `pynput` library
- Replaced ANSI Windows API calls with **Unicode (Wide) Win32 API** via `ctypes`, enabling proper support for multi-language window titles (e.g., Traditional Chinese, Japanese, Korean)
- Introduced dual-mode runtime configuration via GUI dialog — no hardcoded credentials

---

## ✨ Features

| Feature | Description |
|---|---|
| ⌨️ **Real-time Keylogging** | Captures all keystrokes, including Numpad (0–9) and special/function keys |
| 🪟 **Window Tracking** | Logs active window title on focus change (via `pygetwindow`; Unicode supported) |
| 📋 **Clipboard Monitoring** | Automatically captures clipboard content on `Ctrl+V` |
| 🔀 **Dual Operation Modes** | Choose between **Local-Only** (file storage) or **SMTP** (auto email) at startup |
| 👻 **Background Mode** | `.pyw` extension enables silent execution with no console window |
| 📧 **Email Transmission** | Auto-delivers `log.txt` + screenshots via SMTP every **5 minutes** |
| 🛡️ **Fail-Safe Logging** | Local log is only cleared after a **confirmed successful** email delivery |
| 🔒 **Encrypted Transit** | Uses `STARTTLS` (Port 587) — credentials and logs are always encrypted |
| 🔑 **Secure Credentials** | GUI-based App Password input — no secrets hardcoded in source |
| 📸 **Screenshot on Enter** | `(with_screenshotter)` variant captures a screenshot on every `[Enter]` key press, with a **5-second cooldown** to prevent flooding |
| 🗑️ **Auto Screenshot Cleanup** | Screenshots older than **7 days** are automatically deleted to manage disk space |

---

## 📁 File Structure

```
keylogger/
├── keylogger.pyw                      # Core keylogger (keystrokes + clipboard + email)
├── keylogger(with_screenshotter).pyw  # Extended variant with screenshot capture
├── install.bat                        # Automated dependency installer
├── install(with_screenshotter).bat    # Installer for screenshot variant
├── LICENSE
└── README.md
```

---

## ⚙️ Prerequisites

- **OS**: Windows (7 / 10 / 11)
- **Python**: 3.8+ recommended (developed and tested on 3.14; not compatible with Python 2 or 3.5 and below)
- **Core dependencies**: `pynput`, `pywin32`
- **Screenshotter variant extra dependencies**: `pyautogui`, `pygetwindow`

### Python Version Compatibility

| Python Version | Status | Notes |
|---|---|---|
| 3.8 – 3.14 | ✅ Fully supported | Recommended range |
| 3.6 – 3.7 | ⚠️ Partial | May work, but requires pinning older `pynput` version |
| 3.5 and below | ❌ Not supported | f-string syntax causes `SyntaxError` |
| 2.x | ❌ Not supported | Incompatible entirely |

> [!NOTE]
> The project name `v3.14` reflects the development environment. The code itself uses no Python 3.14-exclusive syntax and runs on any **Python 3.8+** installation.

### Option 1 — Automated Setup *(Recommended)*

Double-click `install.bat` for the core keylogger, or `install(with_screenshotter).bat` for the screenshot variant.  
The script will install all dependencies and run the required `pywin32` post-install step automatically.

### Option 2 — Manual Setup

**Core keylogger:**

```batch
py -m pip install pynput pywin32
py -m pywin32_postinstall -install
```

**Screenshotter variant (additional packages):**

```batch
py -m pip install pyautogui pygetwindow
```

---

## 📧 Gmail App Password Setup

To use the SMTP auto-email feature with Gmail:

1. Enable **2-Step Verification** on your Google Account  
   → [myaccount.google.com/security](https://myaccount.google.com/security)
2. Navigate to **Security → App Passwords**
3. Generate a new **16-digit App Password** (select "Mail" and your device)
4. Use this password when the program prompts at startup

> [!TIP]
> Use a dedicated **"burner" Gmail account** for testing to isolate risk and keep your personal account clean.

---

## 🚀 Usage

1. Run `keylogger.pyw` — a configuration dialog will appear
2. Select your operation mode:
   - **Local Only** — logs saved to `log.txt` in the script directory
   - **SMTP Mode** — enter your receiver email and 16-digit App Password
3. The program runs silently in the background
4. In SMTP mode, check your inbox every ~10 minutes for the `Keylogger Report`

**To terminate:** Open **Task Manager** (`Ctrl+Shift+Esc`) → find `pythonw.exe` → End Task

---

## 📸 Screenshotter Variant

`keylogger(with_screenshotter).pyw` extends the core keylogger with automatic screenshot capabilities.

### How It Works

| Behaviour | Detail |
|---|---|
| **Trigger** | A screenshot is captured on every `[Enter]` key press |
| **Cooldown** | 5-second cooldown between captures to prevent screenshot flooding |
| **Skipped capture** | If cooldown is active, a `[ Screenshot skipped: wait Xs ]` note is written to the log |
| **Save location** | Same directory as the script, named `screenshot_YYYYMMDD_HHMMSS.png` |
| **Email attachment** | Screenshots taken within the last 5 minutes are attached to each SMTP report |
| **Auto cleanup** | Screenshots older than **7 days** are automatically deleted on each report cycle |

### Additional Dependency

```batch
py -m pip install pyautogui pygetwindow
```

Or simply run `install(with_screenshotter).bat`.

### Log Example (with screenshots)

```
[ Window: Google Chrome - 搜尋 ]
python keylogger tutorial[ENTER]
[ Screenshot saved: C:\...\screenshot_20260604_143022.png ]

[ Screenshot skipped: wait 3s ]
another search[ENTER]
[ Screenshot saved: C:\...\screenshot_20260604_143028.png ]
```

---

## 🔁 Auto-Start on Windows Boot

### Method 1 — Startup Folder *(Simplest)*

```
Win + R → shell:startup
```

Place `keylogger.pyw` (or a shortcut) in this folder.

> ✅ No admin rights required  
> ⚠️ Only runs after user login; current user only

---

### Method 2 — Task Scheduler *(Recommended)*

1. Open **Task Scheduler** → **Create Basic Task**
2. Trigger: `When the computer starts` or `When I log on`
3. Action: `Start a program`
4. Program: `pythonw.exe`
5. Arguments: `C:\full\path\to\keylogger.pyw`

> ✅ Supports delayed start (useful for network initialization)  
> ✅ Can run without any user logged in

---

### Method 3 — Registry Run Key

```
Win + R → regedit
```

Navigate to:
```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
```

Add a new **String Value**:
- Name: `KeyloggerService` (or any identifier)
- Value: `"C:\Windows\py.exe" "C:\path\to\keylogger.pyw"`

> ✅ Lightweight and persistent  
> ⚠️ Modify the registry with care

---

### Method Comparison

| Method | Requires Login | Admin Required | Best For |
|---|---|---|---|
| Startup Folder | ✅ Yes | ❌ No | Quick testing |
| Task Scheduler | Optional | ✅ Yes | Production / stable use |
| Registry | ✅ Yes | ❌ No | Lightweight persistent setup |

---

## 📄 Log Format

Each session log (`log.txt`) follows this structure:

```
[ PID: 1234 - notepad.exe - 無標題 - 記事本 ]
Hello world! [Enter]

[ PID: 5678 - chrome.exe - Google 搜尋 ]
How to use Python [Enter]

[PASTE] - https://github.com/091cc/keylogger
```

- **Header block**: PID · Executable name · Window title (full Unicode support)
- **Keystroke body**: Raw input including special keys in `[brackets]`
- **Clipboard entries**: Prefixed with `[PASTE]` on every `Ctrl+V` event

---

## 🔧 Technical Notes

- **Unicode Support**: Uses `GetWindowTextW` and `GetForegroundWindow` via `ctypes` to correctly capture CJK and other non-ASCII window titles
- **Event Backend**: `pynput` replaces the unmaintained `pyWinhook`, providing better compatibility with modern Python versions
- **SMTP Security**: All email transmissions use `STARTTLS` on port 587 — plaintext transmission is never used
- **No Hardcoded Secrets**: Credentials are entered at runtime via GUI and never written to disk
- **Screenshot Engine**: Uses `pyautogui.screenshot()` — captures the full screen; saved as PNG with timestamp filename
- **Window Detection (screenshotter)**: Uses `pygetwindow.getActiveWindow()` instead of raw `ctypes` for cleaner cross-version compatibility in the extended variant
- **SMTP Attachments**: Screenshots are sent as `application/octet-stream` MIME attachments and deleted locally after successful delivery
- **Cooldown Logic**: Screenshot cooldown is tracked via `datetime.timedelta` — skipped captures are logged with remaining wait time

---

## 📚 Reference

- [Black Hat Python, 2nd Edition — No Starch Press](https://nostarch.com/black-hat-python2E)
- [pynput Documentation](https://pynput.readthedocs.io/)
- [pywin32 on PyPI](https://pypi.org/project/pywin32/)
- [pyautogui Documentation](https://pyautogui.readthedocs.io/)
- [pygetwindow on PyPI](https://pypi.org/project/PyGetWindow/)

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

*Last updated: June 2026 · KEYLOGGER v3.14*

</div>
