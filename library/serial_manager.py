import serial
import time

from library.yaml_manager import YamlManager
from library.log_manager import print_log, typeLog
from library.macro_manager import MacroManager
from library.ui_manager import UIManager

class SerialManager:
    def __init__(self, yaml_manager: YamlManager, macro_manager: MacroManager, ui_manager: UIManager, baudrate: int=115200, debug: bool=False) -> None:
        self.yaml_manager = yaml_manager
        self.macro_manager = macro_manager
        self.baudrate = baudrate
        self.debug = debug
        self.ui_manager = ui_manager

        self.ser = None
        self.current_port = None
        self.stop_flag = False

        self._last_status = False

    # -------------------------

    def connect(self) -> None:
        port = self.yaml_manager.config["serial_port"]

        if port != self.current_port or self.ser is None or not self.ser.is_open:
            self.close()

            if not port:
                self.ui_manager.edit_title(f"Déconnecté (Aucun port selectionné)")
                return

            try:
                self.ser = serial.Serial(port, self.baudrate, timeout=0.1)
                self.current_port = port
                print_log(typeLog.info, f"Connecté à {port}")

                self.ui_manager.edit_title(f"Connecté ({port})")

                self._last_status = True

            except serial.SerialException as e:
                self.ser = None
                self.current_port = None

                if self._last_status :
                    print_log(typeLog.error, f"Impossible d'ouvrir {port} : {e}")
                    self.ui_manager.edit_title(f"Déconnecté ({port})")
                    self._last_status = False

                time.sleep(0.5)

    def close(self) -> None:
        if self.ser:
            try:
                self.ser.close()
            except Exception:
                pass
        self.ser = None
    # -------------------------

    def listen_loop(self) -> None:
        print_log(typeLog.info, f"Début de la loop")
        while not self.stop_flag:

            self.connect()

            if not self.ser:
                time.sleep(0.2)
                continue

            try:
                if self.ser.is_open and self.ser.in_waiting > 0:
                    data = self.ser.readline().decode(errors="ignore").strip()

                    if data:
                        self.macro_manager.execute_actions(data)
                else:
                    time.sleep(0.05)

            except (OSError, serial.SerialException) as e:
                print_log(typeLog.warning, f"Port série déconnecté : {e}")

                # Force la reconnexion
                self.close()
                self.current_port = None
                time.sleep(0.5)

    def stop(self) -> None:
        self.stop_flag = True
