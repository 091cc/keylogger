# KEYLOGGER v3.14

⚠️⚠️⚠️ **LEGAL WARNING** ⚠️⚠️⚠️
This software is provided for **EDUCATIONAL and RESEARCH purposes only**. 
The author is not responsible for any illegal use of this tool. 
This program is designed exclusively for **Windows** operating systems.

## Acknowledgements
This project is a modern, rewritten version of the example found in **[Black Hat Python, 2nd Edition](https://nostarch.com/black-hat-python2E)**. 
- **Major Updates**: Fully compatible with **Python 3.14**.
- **Key Improvements**: Replaced outdated `pyWinhook` with `pynput` for better stability and implemented **Unicode (Wide) Windows API** to support multi-language window titles (e.g., Traditional Chinese).

## Features
* **Real-time Keylogging**: Captures all keystrokes including special keys.
* **Window Tracking**: Logs the Process ID (PID), executable name, and active window title.
* **Clipboard Monitoring**: Automatically captures content when `Ctrl+V` is pressed.
* **Background Mode**: Supports `.pyw` execution for silent operation.

## Building Environment
Ensure you have Python 3.x installed. Run the following commands to set up the dependencies:

```bash
pip install pynput pywin32
python -m pywin32_postinstall -install
