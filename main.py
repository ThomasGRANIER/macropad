import serial
import subprocess
import time
import os
import tkinter as tk
import threading
from tkinter import ttk
import serial.tools.list_ports
import yaml

stop_flag = False
profile = 1
CONFIG_FILE = "macropad_config.yml"
BAUDRATE = 115200
DEBUG = False

# --- Fenêtre configuration ---
def config_window(parent):
    win = tk.Toplevel(parent)
    win.title("Configuration du port")
    win.geometry("400x300")

    ports_listbox = tk.Listbox(win, width=50)
    ports_listbox.pack(padx=10, pady=10, fill="both", expand=True)

    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        ports_listbox.insert(tk.END, f"{p.device} - {p.description} - {p.hwid}")

    # Sélection précédente
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
            saved_port = cfg.get("serial_port", "")
            for i, p in enumerate(ports):
                if p.device == saved_port:
                    ports_listbox.selection_set(i)
                    break

    def save_selection():
        sel = ports_listbox.curselection()
        if sel:
            chosen_port = ports[sel[0]].device
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                yaml.dump({"serial_port": chosen_port}, f)
            win.destroy()

    save_btn = ttk.Button(win, text="Enregistrer", command=save_selection)
    save_btn.pack(pady=5)

# --- Gestion macros ---
def load_yaml(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_macro_name(pos):
    filename = f"profiles/{profile}/{pos}.yml"
    if not os.path.exists(filename):
        return ""
    try:
        data = load_yaml(filename) or {}
        return data.get("name", "")
    except:
        return ""

def show_macro_grid():
    root = tk.Tk()
    root.title("Disposition du macropad")
    root.geometry("1000x500")

    # Frame principal
    frame = ttk.Frame(root, padding=10)
    frame.pack(fill="both", expand=True)

    if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
                max_row = cfg.get("nb_ligne")
                max_col = cfg.get("nb_column")

    # Crée une frame pour le grid + bouton en haut
    top_frame = ttk.Frame(frame)
    top_frame.pack(fill="both", expand=True)

    grid_tools = ttk.LabelFrame(top_frame, text="Tools")
    grid_tools.pack(side="right", fill="both", expand=True)

    grid_frame = ttk.Frame(top_frame)
    grid_frame.pack(side="left", fill="both", expand=True)

    # Bouton engrenage en haut à droite
    def open_config():
        config_window(root)

    gear_button = ttk.Button(grid_tools, text="⚙", command=open_config)
    gear_button.pack(side="top", anchor="n", padx=5, pady=5)

    # Création de la grille de macros
    for l in range(1, max_row + 1):
        for c in range(1, max_col + 1):
            pos = f"l{l}c{c}"
            label_frame = ttk.LabelFrame(grid_frame, text=pos.upper(), padding=5)
            label_frame.grid(row=l - 1, column=c - 1, padx=3, pady=3, sticky="nsew")
            name_label = ttk.Label(label_frame, text=get_macro_name(pos), anchor="center", wraplength=180)
            name_label.pack(expand=True, fill="both")

    # Grille redimensionnable
    for i in range(max_row):
        grid_frame.rowconfigure(i, weight=1, uniform="row")
    for j in range(max_col):
        grid_frame.columnconfigure(j, weight=1, uniform="col")

    # Fermeture propre
    def on_close():
        global stop_flag
        stop_flag = True
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

# --- Boucle écoute série ---
def listen_loop():
    global stop_flag
    ser = None
    current_port = None

    while not stop_flag:
        # Lire port actuel
        port = None
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
                port = cfg.get("serial_port")

        # Reconnecter si port changé ou ser fermé
        if port != current_port or ser is None or not ser.is_open:
            if ser:
                try: ser.close()
                except: pass
            if port:
                try:
                    ser = serial.Serial(port, BAUDRATE, timeout=0.1)
                    current_port = port
                    print(f"[INFO] Connecté à {port}")
                except serial.SerialException as e:
                    ser = None
                    current_port = None
                    print(f"[ERREUR] Impossible d'ouvrir {port} : {e}")
                    time.sleep(0.5)
                    continue
            else:
                ser = None
                current_port = None
                time.sleep(0.5)
                continue

        # Lecture série si connecté
        if ser and ser.is_open and ser.in_waiting > 0:
            data = ser.readline().decode(errors="ignore").strip()
            if not data:
                continue
            yaml_file = f"profiles/{profile}/{data}.yml"
            if not os.path.exists(yaml_file):
                if DEBUG: print(f"[INFO] Aucun fichier YAML pour {data}")
                continue
            try:
                action_config = load_yaml(yaml_file)
            except Exception as e:
                print(f"[ERREUR] Échec du chargement de {yaml_file} : {e}")
                continue

            for cmd in action_config.get("actions", []):
                action_type = cmd.get("type")
                value = str(cmd.get("value", ""))
                if DEBUG:
                    print(f"[DEBUG] {data} : {action_type} - {value.replace(chr(10),'')}")
                if action_type == "key":
                    subprocess.run(["xdotool", "key", value])
                elif action_type == "text":
                    subprocess.run(["xdotool", "type", value])
                elif action_type == "cmd":
                    subprocess.Popen(value, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif action_type == "delay":
                    try: time.sleep(int(value)/1000)
                    except: pass
        else:
            time.sleep(0.05)

    if ser:
        try: ser.close()
        except: pass
    print("[INFO] Arrêt du script suite à la fermeture de la GUI")

# --- Main ---
if __name__ == "__main__":
    threading.Thread(target=show_macro_grid, daemon=True).start()
    listen_loop()
