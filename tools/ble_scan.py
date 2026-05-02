import asyncio
from bleak import BleakScanner


async def scan():
    print("Scan BLE en cours (10 secondes)...\n")
    devices = await BleakScanner.discover(timeout=10.0, return_adv=True)

    if not devices:
        print("Aucun appareil trouvé.")
        return

    for addr, (device, adv) in devices.items():
        print(f"Adresse  : {device.address}")
        print(f"Nom      : {device.name}")
        print(f"Nom adv  : {adv.local_name}")
        print(f"Services : {adv.service_uuids}")
        print(f"RSSI     : {adv.rssi} dBm")
        print("-" * 40)


asyncio.run(scan())
