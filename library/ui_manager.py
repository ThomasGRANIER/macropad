import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
import serial.tools.list_ports

from library.yaml_manager import YamlManager
from library.serial_manager import SerialManager


class UIManager:
    def __init__(self, yaml_manager: YamlManager, serial_manager: SerialManager):
        self.yaml_manager = yaml_manager
        self.serial_manager = serial_manager

        # IMPORTANT : ne PAS créer tk.Tk() avant
        self.root = ttk.Window(themename="darkly")

        self.labels = {}
    # -------------------------

    def open_config_window(self) -> None:
        win = tk.Toplevel(self.root)
        win.title("Configuration du port")
        win.geometry("500x400")

        # Frame principale
        main_frame = ttk.Frame(win)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ports_listbox = tk.Listbox(main_frame)
        ports_listbox.pack(fill="both", expand=True)

        # On stocke la liste courante des ports
        ports = []

        # -------------------------
        # Refresh function
        # -------------------------
        def refresh_ports():
            nonlocal ports

            # Sauvegarde sélection actuelle
            selected_device = None
            sel = ports_listbox.curselection()
            if sel and sel[0] < len(ports):
                selected_device = ports[sel[0]].device

            ports_listbox.delete(0, tk.END)
            ports = list(serial.tools.list_ports.comports())

            for p in ports:
                ports_listbox.insert(
                    tk.END,
                    f"{p.device} - {p.description} - {p.hwid}"
                )

            # Restaure sélection sauvegardée
            if selected_device:
                for i, p in enumerate(ports):
                    if p.device == selected_device:
                        ports_listbox.selection_set(i)
                        break

            # Sinon sélectionne port sauvegardé en config
            else:
                saved_port = self.yaml_manager.get_serial_port()
                for i, p in enumerate(ports):
                    if p.device == saved_port:
                        ports_listbox.selection_set(i)
                        break

        # -------------------------
        # Save selection
        # -------------------------
        def save_selection():
            sel = ports_listbox.curselection()
            if sel:
                chosen_port = ports[sel[0]].device
                self.yaml_manager.config["serial_port"] = chosen_port
                self.yaml_manager.save_config()
                win.destroy()

        # -------------------------
        # Boutons
        # -------------------------

        buttons_frame = ttk.Frame(win)
        buttons_frame.pack(fill="x", pady=5)

        ttk.Button(
            buttons_frame,
            text="Actualiser",
            bootstyle="outline-info",
            command=refresh_ports
        ).pack(side="left", padx=5)

        ttk.Button(
            buttons_frame,
            text="Enregistrer",
            bootstyle="outline-light",
            command=save_selection
        ).pack(side="right", padx=5)

        # Chargement initial
        refresh_ports()

    # -------------------------

    def refresh_grid_titles(self) -> None:
        for pos, label in self.labels.items():
            new_name = self.yaml_manager.get_macro_name(pos)
            label.config(text=new_name)

    def build_grid(self) -> None:
        self.root.title("Disposition du macropad")
        self.root.geometry("900x500")

        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill="both", expand=True)

        max_row, max_col = self.yaml_manager.get_grid_size()

        top_frame = ttk.Frame(frame)
        top_frame.pack(fill="both", expand=True)

        encoders_frame = ttk.Frame(top_frame)
        encoders_frame.pack(side="left", fill="y", padx=(0, 10))

        grid_frame = ttk.Frame(top_frame)
        grid_frame.pack(side="left", fill="both", expand=True)

        grid_tools = ttk.Frame(top_frame, padding=1)
        grid_tools.pack(side="right", fill="y")

        ttk.Label(
            encoders_frame,
            text="E1",
            font=("Segoe UI", 10, "bold")
        ).pack(pady=(0, 4))

        encoder1_buttons = [
            ("↺", "e1-"),
            ("↻", "e1+"),
            ("⏺", "e1b"),
        ]

        for text, key in encoder1_buttons:
            ttk.Button(
                encoders_frame,
                text=text,
                bootstyle="outline-light",
                command=lambda k=key: self.yaml_manager.open_editor(k)
            ).pack(fill="x", pady=3)

        # Séparateur visuel
        ttk.Separator(encoders_frame).pack(fill="x", pady=15)

        ttk.Label(
            encoders_frame,
            text="E2",
            font=("Segoe UI", 10, "bold")
        ).pack(pady=(0, 4))

        encoder2_buttons = [
            ("↺", "e2-"),
            ("↻", "e2+"),
            ("⏺", "e2b"),
        ]

        for text, key in encoder2_buttons:
            ttk.Button(
                encoders_frame,
                text=text,
                bootstyle="outline-light",
                command=lambda k=key: self.yaml_manager.open_editor(k)
            ).pack(fill="x", pady=3)

        ttk.Label(
            grid_tools,
            text="🛠",
            font=("Segoe UI", 14)
        ).pack(side="top", pady=(0, 4))

        ttk.Button(
            grid_tools,
            text="⟳",
            bootstyle="outline-light",
            command=self.refresh_grid_titles
        ).pack(side="top", fill="x", padx=5, pady=(0, 5))

        ttk.Button(
            grid_tools,
            text="⚙",
            bootstyle="outline-light",
            command=self.open_config_window
        ).pack(side="top", anchor="s", padx=5, pady=(2, 5), fill="x")

        ttk.Button(
            grid_tools,
            text="X",
            bootstyle="outline-light",
            command=self.root.destroy
        ).pack(side="bottom", anchor="n", padx=5, pady=(2, 5), fill="x")

        for l in range(1, max_row + 1):
            for c in range(1, max_col + 1):
                pos = f"l{l}c{c}"
                button = ttk.Button(
                    grid_frame,
                    text=self.yaml_manager.get_macro_name(pos),
                    bootstyle="outline-light",
                    command=lambda p=pos: self.yaml_manager.open_editor(p)
                )

                button.grid(
                    row=l - 1,
                    column=c - 1,
                    padx=6,
                    pady=6,
                    sticky="nsew"
                )
                self.labels[pos] = button

        for i in range(max_row):
            grid_frame.rowconfigure(i, weight=1, uniform="row")

        for j in range(max_col):
            grid_frame.columnconfigure(j, weight=1, uniform="col")

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # -------------------------

    def on_close(self) -> None:
        self.serial_manager.stop()
        self.root.destroy()

    def run(self) -> None:
        self.build_grid()
        self.root.mainloop()
