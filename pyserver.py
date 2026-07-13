#!/usr/bin/env python3
import tkinter as tk
from tkinter import scrolledtext




import server_functions as sf
from server_functions import on_close, save_log, init_db, get_logs, start_server, stop_server, show_status, open_mainpage, show_logs, clear_logs, open_settings, save_settings



root = tk.Tk()
root.geometry("800x300")
root.title("PyServer V 0.1 - Server di gestione e monitoraggio")

sf.init_db()

menubar = tk.Menu(root)
file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(
    label="Avvia Server", 
command=lambda: sf.start_server(status_label, output_screen)
)
file_menu.add_command(
    label="Ferma Server", 
    command=lambda: sf.stop_server(status_label, output_screen)
)
file_menu.add_command(
    label="Settings",
    command=lambda: sf.open_settings()
)

file_menu.add_separator()

file_menu.add_command(
    label="Esci", 
    command=lambda: sf.on_close(root)
)



server_menu = tk.Menu(menubar, tearoff=0)
server_menu.add_command(
    label="Stato Server", 
    command=lambda: sf.show_status(status_label, output_screen)
)
server_menu.add_command(
    label="Apri Browser", 
    command=sf.open_mainpage
)
server_menu.add_separator()
logs_menu = tk.Menu(menubar, tearoff=0)
logs_menu.add_command(
    label="Mostra Log", 
    command=lambda: sf.show_logs(output_screen)
)
logs_menu.add_command(
    label="Pulisci Log", 
    command=lambda: sf.clear_logs(output_screen)
)

help_menu = tk.Menu(menubar, tearoff=0)
help_menu.add_command(
    label="Info",
    command=lambda: sf.info()
)


menubar.add_cascade(label="File", menu=file_menu)
menubar.add_cascade(label="Server", menu=server_menu)
menubar.add_cascade(label="Logs", menu=logs_menu)
menubar.add_cascade(label="Help", menu=help_menu)
root.config(menu=menubar)


output_screen = scrolledtext.ScrolledText(root,bg="black", fg="white", wrap=tk.WORD, width=100, height=10)
output_screen.pack(pady=10, padx=10, fill="both", expand=True)
output_screen.insert(tk.END, "Benvenuto in PyServer V 0.1\n [Server di gestione e monitoraggio]\n ===============================\n Creato da: Edmondo Piazza\n Email: epartstudio2017@gmail.com\n ===============================\n")
#output_screen.delete("1.0", tk.END)

status_label = tk.Label(root, text="Server non attivo", fg="red")
status_label.pack(pady=5)

root.protocol("WM_DELETE_WINDOW", lambda: sf.on_close(root))
root.mainloop()