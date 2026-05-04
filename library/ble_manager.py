import asyncio
from bleak import BleakScanner, BleakClient

from library.log_manager import print_log, typeLog
from library.macro_manager import MacroManager
from library.ui_manager import UIManager
from library.yaml_manager import YamlManager

DEVICE_NAME = "SimplePAD"
UART_TX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
UART_SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
BATTERY_LEVEL_UUID = "00002a19-0000-1000-8000-00805f9b34fb"


class BLEManager:
    def __init__(self, yaml_manager: YamlManager, macro_manager: MacroManager, ui_manager: UIManager) -> None:
        self.yaml_manager = yaml_manager
        self.macro_manager = macro_manager
        self.ui_manager = ui_manager
        self.stop_flag = False
        self._connected = False
        self._battery_level: int | None = None
        self._loop = None

    @property
    def is_connected(self) -> bool:
        return self._connected

    def _update_title(self) -> None:
        if self._battery_level is not None:
            self.ui_manager.edit_title(f"Connecté BLE ({DEVICE_NAME}) | {self._battery_level}%")
        else:
            self.ui_manager.edit_title(f"Connecté BLE ({DEVICE_NAME})")

    def _on_notification(self, sender, data: bytearray) -> None:
        for msg in data.decode("utf-8", errors="ignore").split("\n"):
            msg = msg.strip()
            if msg:
                self.macro_manager.execute_actions(msg)

    def _on_battery_notification(self, sender, data: bytearray) -> None:
        self._battery_level = int(data[0])
        self._update_title()

    async def _find_device(self) -> object:
        print_log(typeLog.info, "BLE: Scan en cours...")
        try:
            devices = await BleakScanner.discover(timeout=5.0, return_adv=True)
            device = next(
                (d for d, adv in devices.values()
                 if adv.local_name == DEVICE_NAME or d.name == DEVICE_NAME
                 or UART_SERVICE_UUID in adv.service_uuids),
                None
            )
            if device:
                return device
        except Exception as e:
            print_log(typeLog.error, f"BLE: Erreur scan : {e}")

        return None

    async def _run_async(self) -> None:
        while not self.stop_flag:
            target = await self._find_device()

            if not target:
                await asyncio.sleep(2)
                continue

            print_log(typeLog.info, f"BLE: Connexion à {target}...")
            try:
                async with BleakClient(target) as client:
                    self._connected = True
                    self._battery_level = None

                    # Lecture initiale de la batterie
                    try:
                        data = await client.read_gatt_char(BATTERY_LEVEL_UUID)
                        self._battery_level = int(data[0])
                        print_log(typeLog.info, f"BLE: Batterie initiale : {self._battery_level}%")
                    except Exception as e:
                        print_log(typeLog.warning, f"BLE: Lecture batterie échouée : {e}")

                    self._update_title()
                    print_log(typeLog.info, f"BLE: Connecté à {DEVICE_NAME}")

                    await client.start_notify(UART_TX_UUID, self._on_notification)

                    # Souscription aux notifications batterie si supporté
                    try:
                        await client.start_notify(BATTERY_LEVEL_UUID, self._on_battery_notification)
                        battery_notify = True
                    except Exception as e:
                        print_log(typeLog.warning, f"BLE: Notifications batterie non supportées : {e}")
                        battery_notify = False

                    while not self.stop_flag and client.is_connected:
                        await asyncio.sleep(0.1)

                    await client.stop_notify(UART_TX_UUID)
                    if battery_notify:
                        await client.stop_notify(BATTERY_LEVEL_UUID)

            except Exception as e:
                print_log(typeLog.error, f"BLE: Erreur connexion : {e}")
            finally:
                self._connected = False
                self._battery_level = None
                if not self.stop_flag:
                    print_log(typeLog.warning, "BLE: Déconnecté")
                    self.ui_manager.edit_title("Déconnecté BLE")

            await asyncio.sleep(1)

    def listen_loop(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._run_async())
        finally:
            self._loop.close()

    def stop(self) -> None:
        self.stop_flag = True
