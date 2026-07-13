import subprocess
import sqlite3
from tkinter import filedialog
import webbrowser
from datetime import datetime
import os
import tkinter as tk
from tkinter import messagebox

server_process = None
PORT = "8000"
SERVICE_NAME = "PyServer"
DIRECTORY = "."
DB_PATH = "data/server_logs.db"

def init_db():
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            level TEXT NOT NULL,
            action TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_log(level, action, message):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO logs (timestamp, level, action, message)
        VALUES (?, ?, ?, ?)
    """, (timestamp, level, action, message))

    conn.commit()
    conn.close()

def get_logs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, level, action, message
        FROM logs
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows

def open_settings():
    settings_window = tk.Toplevel()
    settings_window.title("Impostazioni")
    settings_window.geometry("400x380")
    settings_window.resizable(False, False)

    name_label = tk.Label(settings_window, text="Nome servizio:")
    name_label.pack(pady=(20, 10))

    name_service_entry = tk.Entry(settings_window)
    name_service_entry.insert(0, SERVICE_NAME)
    name_service_entry.pack(pady=5)

    port_label = tk.Label(settings_window, text="Porta:")
    port_label.pack(pady=(20, 5))

    port_entry = tk.Entry(settings_window)
    port_entry.insert(0, str(PORT))
    port_entry.pack(pady=5)

    directory_label = tk.Label(settings_window, text="Directory:")
    directory_label.pack(pady=(20, 5))

    directory_frame = tk.Frame(settings_window)
    directory_frame.pack(pady=5)

    directory_entry = tk.Entry(directory_frame, width=30)
    directory_entry.insert(0, DIRECTORY)
    directory_entry.pack(side="left", padx=5)

    browse_button = tk.Button(
        directory_frame,
        text="Sfoglia",
        command=lambda: choose_directory(directory_entry)
    )
    browse_button.pack(side="left")    

    directory_entry = tk.Entry(settings_window)
    directory_entry.insert(0, DIRECTORY)
    directory_entry.pack(pady=5)

    btn_save = tk.Button(
        settings_window,
        text="Salva impostazioni",
        command=lambda: save_settings(
            name_service_entry,
            port_entry,
            directory_entry,
            settings_window
        )
    )
    btn_save.pack(pady=20)

def choose_directory(directory_entry):
    selected_directory = filedialog.askdirectory()
    if selected_directory:
        directory_entry.delete(0, tk.END)
        directory_entry.insert(0, selected_directory)

def save_settings(name_service_entry, port_entry, directory_entry, settings_window):
    global PORT, SERVICE_NAME, DIRECTORY

    service_name = name_service_entry.get().strip()
    port = port_entry.get().strip()
    directory = directory_entry.get().strip()

    if not service_name:
        service_name = "PyServer"

    if not port:
        messagebox.showwarning("Attenzione", "Inserisci una porta.")
        return

    if not port.isdigit():
        messagebox.showerror("Errore", "La porta deve essere numerica.")
        return

    if not directory:
        directory = "."

    PORT = port
    SERVICE_NAME = service_name
    DIRECTORY = directory

    save_log(
        "INFO",
        "settings",
        f"Impostazioni salvate: service={SERVICE_NAME}, port={PORT}, directory={DIRECTORY}"
    )

    settings_window.destroy()


def start_server(status_label, output_screen):
    global server_process, PORT, SERVICE_NAME, DIRECTORY

    port = str(PORT).strip()

    if not port:
        status_label.config(text="Inserisci una porta valida", fg="red")
        save_log("ERROR", "start", "Tentativo di avvio senza porta specificata")
        return

    if not port.isdigit() or not (1 <= int(port) <= 65535):
        status_label.config(
            text="Porta non valida. Inserisci un numero tra 1 e 65535.",
            fg="red"
        )
        save_log("ERROR", "start", f"Porta non valida: {port}")
        return

    if server_process is not None and server_process.poll() is None:
        status_label.config(text="Server già attivo", fg="orange")
        save_log("INFO", "start", "Tentativo di avvio con server già attivo")
        return

    try:
        server_process = subprocess.Popen(
            ["python3", "-m", "http.server", port],
            cwd=DIRECTORY
        )

        status_label.config(
            text=f"{SERVICE_NAME} attivo su http://localhost:{port}",
            fg="green"
        )

        show_output(
            output_screen,
            f"{SERVICE_NAME} avviato su http://localhost:{port}\nDirectory: {DIRECTORY}"
        )

        save_log(
            "INFO",
            "start",
            f"Servizio '{SERVICE_NAME}' avviato sulla porta {port} nella directory {DIRECTORY}"
        )

    except Exception as e:
        status_label.config(text=f"Errore avvio server: {e}", fg="red")
        show_output(output_screen, f"Errore avvio server: {e}")
        save_log("ERROR", "start", f"Errore avvio server: {e}")


def show_logs(output_screen):
    logs = get_logs()
    output_screen.delete("1.0", tk.END)

    if not logs:
        output_screen.insert(tk.END, "Nessun log presente.\n")
        return

    for log in logs:
        timestamp, level, action, message = log
        line = f"[{timestamp}] {level} | {action} | {message}\n"
        output_screen.insert(tk.END, line)

def clear_logs(output_screen):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM logs")

    conn.commit()
    conn.close()

    output_screen.delete("1.0", tk.END)
    output_screen.insert(tk.END, "Tutti i log sono stati cancellati.\n")
    save_log("INFO", "clear_logs", "Tutti i log sono stati cancellati")


def stop_server(status_label, output_screen):
    global server_process

    if server_process is None or server_process.poll() is not None:
        status_label.config(text="Nessun server attivo", fg="orange")
        save_log("WARNING", "stop", "Tentativo di stop senza server attivo")
        return

    try:
        server_process.terminate()
        server_process.wait()
        server_process = None
        status_label.config(text="Server fermato", fg="red")
        show_output(output_screen, "Server fermato correttamente")
        save_log("INFO", "stop", "Server fermato correttamente")
    except Exception as e:
        status_label.config(text=f"Errore arresto server: {e}", fg="red")
        show_output(output_screen, f"Errore arresto server: {e}")
        save_log("ERROR", "stop", f"Errore arresto server: {e}")


def show_status(status_label, output_screen):
    if server_process is not None and server_process.poll() is None:
        status_label.config(
            text=f"{SERVICE_NAME} attivo su http://localhost:{PORT}",
            fg="green"
        )
        show_output(
            output_screen,
            f"{SERVICE_NAME} attivo su http://localhost:{PORT}\nDirectory: {DIRECTORY}"
        )
        save_log("INFO", "status", "Controllo stato: server attivo")
    else:
        status_label.config(text="Server non attivo", fg="red")
        show_output(output_screen, "Server non attivo")
        save_log("INFO", "status", "Controllo stato: server non attivo")


def show_output(output_screen, text):
    output_screen.delete("1.0", tk.END)
    output_screen.insert(tk.END, text)


def open_mainpage():
    if server_process is not None and server_process.poll() is not None:
        save_log("WARNING", "open_page", "Tentativo di apertura homepage con server spento")
        return

    if server_process is not None and server_process.poll() is None:
        webbrowser.open(f"http://localhost:{PORT}/")
        save_log("INFO", "open_page", f"Homepage di '{SERVICE_NAME}' aperta nel browser")


def on_close(root):
    global server_process

    if server_process is not None and server_process.poll() is None:
        server_process.terminate()
        server_process.wait()
        save_log("INFO", "close", "Applicazione chiusa con arresto del server")
    
    root.destroy()


def info():
    window = tk.Toplevel()
    window.title("Informazioni su PyServer")
    window.geometry("420x260")
    window.resizable(False, False)

    title_label = tk.Label(
        window,
        text="PyServer",
        font=("Arial", 16, "bold")
    )
    title_label.pack(pady=(20, 5))

    version_label = tk.Label(
        window,
        text="v0.1",
        font=("Arial", 10)
    )
    version_label.pack()

    desc_label = tk.Label(
        window,
        text="Utility grafica per la gestione di un server HTTP locale\n"
             "basato su Python.",
        font=("Arial", 11),
        justify="center"
    )
    desc_label.pack(pady=15)

    author_label = tk.Label(
        window,
        text="git username: @Ed1628",
        font=("Arial", 10)
    )
    author_label.pack()

    close_btn = tk.Button(window, text="Chiudi", command=window.destroy)
    close_btn.pack(pady=20)