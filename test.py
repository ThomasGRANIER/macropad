import asyncio
from bleak import BleakScanner, BleakClient

DEVICE_NAME = "MonMacropad"

async def main():
    devices = await BleakScanner.discover()
    target = None
    for d in devices:
        if d.name == DEVICE_NAME:
            target = d
            break
    if not target:
        print("Appareil non trouvé")
        return

    async with BleakClient(target) as client:
        print("Connecté à", DEVICE_NAME)
        
        # UART Service Nordic
        UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
        UART_RX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # notifications
        
        def handle_rx(sender, data):
            print("Reçu :", data.decode("utf-8").strip())
        
        await client.start_notify(UART_RX_CHAR_UUID, handle_rx)
        
        print("En écoute... Ctrl+C pour quitter")
        while True:
            await asyncio.sleep(1)

asyncio.run(main())