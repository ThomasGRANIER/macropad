import time
import board
import keypad
import rotaryio
from digitalio import DigitalInOut, Direction, Pull
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

# === Initialisation BLE ===
ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)
advertisement.complete_name = "SimplePAD"
ble.start_advertising(advertisement)

# === Clavier matrice ===
row_pins = (board.P0_17, board.P0_11, board.P1_04, board.P1_06)
col_pins = (board.P0_20, board.P0_22, board.P0_24, board.P1_00)
keys = keypad.KeyMatrix(row_pins=row_pins, column_pins=col_pins, columns_to_anodes=True)
num_cols = len(col_pins)

# === Encodeur 1 ===
encoder1 = rotaryio.IncrementalEncoder(board.P0_02, board.P1_13)
last_position1 = encoder1.position
button1 = DigitalInOut(board.P1_15)
button1.direction = Direction.INPUT
button1.pull = Pull.UP
button1_last = button1.value

# === Encodeur 2 ===
encoder2 = rotaryio.IncrementalEncoder(board.P1_11, board.P0_09)
last_position2 = encoder2.position
button2 = DigitalInOut(board.P0_10)
button2.direction = Direction.INPUT
button2.pull = Pull.UP
button2_last = button2.value

# === Timer pour flush des événements ===
last_flush = time.monotonic()
flush_interval = 0.05  # 50 ms

# === Buffer des événements ===
event_buffer = []

while True:
    # --- BLE : démarrer la publicité si non connecté ---
    if not ble.connected and not ble.advertising:
        ble.start_advertising(advertisement)

    # --- Clavier ---
    event = keys.events.get()
    if event:
        row = event.key_number % num_cols + 1
        col = event.key_number // num_cols + 1
        if event.pressed:
            event_buffer.append(f"l{row}c{col}")

    # --- Encodeur 1 ---
    pos1 = encoder1.position
    if pos1 != last_position1:
        direction = "-" if pos1 > last_position1 else "+"
        event_buffer.append(f"E1{direction}")
        last_position1 = pos1

    # --- Encodeur 2 ---
    pos2 = encoder2.position
    if pos2 != last_position2:
        direction = "-" if pos2 > last_position2 else "+"
        event_buffer.append(f"E2{direction}")
        last_position2 = pos2

    # --- Bouton 1 ---
    if button1.value != button1_last:
        time.sleep(0.01)  # debounce
        if not button1.value:
            event_buffer.append("E1B")
        button1_last = button1.value

    # --- Bouton 2 ---
    if button2.value != button2_last:
        time.sleep(0.01)
        if not button2.value:
            event_buffer.append("E2B")
        button2_last = button2.value

    # --- Flush buffer toutes les 50ms ---
    now = time.monotonic()
    if now - last_flush >= flush_interval and event_buffer:
        for msg in event_buffer:
            if ble.connected:
                try:
                    uart.write((msg + "\n").encode("utf-8"))
                    print(f"test : msg")
                except Exception as e:
                    print("BLE Error:", e)
            else:
                print(msg)
        event_buffer = []
        last_flush = now

    time.sleep(0.005)  # petite pause pour soulager le CPU
