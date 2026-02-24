import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports

from library.yaml_manager import YamlManager
from library.serial_manager import SerialManager


class UIManager:
    def __init__(self, yaml_manager: YamlManager, serial_manager: SerialManager):
        self.yaml_manager = yaml_manager
        self.serial_manager = serial_manager
        self.root = tk.Tk()

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

        ttk.Button(win, text="Enregistrer",
                   command=save_selection).pack(pady=5)

    # -------------------------

    def build_grid(self) -> None:
        self.root.title("Disposition du macropad")
        self.root.geometry("1000x500")

        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill="both", expand=True)

        max_row, max_col = self.yaml_manager.get_grid_size()

        top_frame = ttk.Frame(frame)
        top_frame.pack(fill="both", expand=True)

        grid_tools = ttk.LabelFrame(top_frame, text="Tools")
        grid_tools.pack(side="right", fill="both", expand=True)

        grid_frame = ttk.Frame(top_frame)
        grid_frame.pack(side="left", fill="both", expand=True)

        ttk.Button(
            grid_tools,
            text="⚙",
            command=self.open_config_window
        ).pack(side="top", anchor="n", padx=5, pady=5)

        for l in range(1, max_row + 1):
            for c in range(1, max_col + 1):
                pos = f"l{l}c{c}"
                label_frame = ttk.LabelFrame(
                    grid_frame,
                    text=pos.upper(),
                    padding=5
                )
                label_frame.grid(
                    row=l - 1,
                    column=c - 1,
                    padx=3,
                    pady=3,
                    sticky="nsew"
                )

                name_label = ttk.Label(
                    label_frame,
                    text=self.yaml_manager.get_macro_name(pos),
                    anchor="center",
                    wraplength=180
                )
                name_label.pack(expand=True, fill="both")

        for i in range(max_row):
            grid_frame.rowconfigure(i, weight=1)

        for j in range(max_col):
            grid_frame.columnconfigure(j, weight=1)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # -------------------------

    def on_close(self) -> None:
        self.serial_manager.stop()
        self.root.destroy()

    def run(self) -> None:
        self.build_grid()
        self.root.mainloop()
