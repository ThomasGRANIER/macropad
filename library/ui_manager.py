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

        ports_listbox = tk.Listbox(win, width=50)
        ports_listbox.pack(padx=10, pady=10, fill="both", expand=True)

        ports = list(serial.tools.list_ports.comports())

        for p in ports:
            ports_listbox.insert(
                tk.END,
                f"{p.device} - {p.description} - {p.hwid}"
            )

        saved_port = self.yaml_manager.get_serial_port()

        for i, p in enumerate(ports):
            if p.device == saved_port:
                ports_listbox.selection_set(i)
                break

        def save_selection():
            sel = ports_listbox.curselection()
            if sel:
                chosen_port = ports[sel[0]].device
                self.yaml_manager.config["serial_port"] = chosen_port
                self.yaml_manager.save_config()
                win.destroy()

        ttk.Button(win, text="Enregistrer",bootstyle="outline-light",
                   command=save_selection).pack(pady=5)

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

        grid_tools = ttk.Label(top_frame)
        grid_tools.pack(side="right", fill="both", expand=True)

        grid_frame = ttk.Frame(top_frame)
        grid_frame.pack(side="left", fill="both", expand=True)

        ttk.Button(
            grid_tools,
            text="↻",
            bootstyle="outline-light",
            command=self.refresh_grid_titles
        ).pack(side="top", anchor="n", padx=5, pady=(5, 2), fill="x")

        ttk.Button(
            grid_tools,
            text="⚙",
            bootstyle="outline-light",
            command=self.open_config_window
        ).pack(side="top", anchor="n", padx=5, pady=(2, 5), fill="x")

        for l in range(1, max_row + 1):
            for c in range(1, max_col + 1):
                pos = f"l{l}c{c}"
                label_frame = ttk.Frame(
                    grid_frame,
                    bootstyle="secondary",
                    padding=1,
                    borderwidth=1,
                    relief="solid"
                )
                label_frame.grid(
                    row=l - 1,
                    column=c - 1,
                    padx=6,
                    pady=6,
                    sticky="nsew"
                )

                name_label = ttk.Label(
                    label_frame,
                    text=self.yaml_manager.get_macro_name(pos),
                    anchor="center",
                    wraplength=180
                )
                name_label.pack(expand=True, fill="both")
                self.labels[pos] = name_label

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
