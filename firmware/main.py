import time
import board
import keypad
import rotaryio
from digitalio import DigitalInOut, Direction, Pull
from adafruit_ble import BLERadio
from adafruit_ble.services.standard import BatteryService
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

#vbat_pin = analogio.AnalogIn(board.BAT_VOLT)  # pin batterie du nice!nano_raw_history = []

def read_battery_percent():
    import analogio
    pin = analogio.AnalogIn(board.BAT_VOLT)
    time.sleep(0.1)
    samples = []
    for _ in range(5):
        samples.append(pin.value)
        time.sleep(0.02)
    pin.deinit()
    s = sorted(samples)[1:-1]
    raw = sum(s) / len(s)
    voltage = (raw / 4095) * 7.152

    # Courbe Li-Po 3.7V nominale (902030)
    if   voltage >= 4.20: percent = 100
    elif voltage >= 4.10: percent = int(90 + (voltage - 4.10) / 0.10 * 10)
    elif voltage >= 3.95: percent = int(75 + (voltage - 3.95) / 0.15 * 15)
    elif voltage >= 3.80: percent = int(55 + (voltage - 3.80) / 0.15 * 20)
    elif voltage >= 3.70: percent = int(40 + (voltage - 3.70) / 0.10 * 15)
    elif voltage >= 3.60: percent = int(25 + (voltage - 3.60) / 0.10 * 15)
    elif voltage >= 3.40: percent = int(10 + (voltage - 3.40) / 0.20 * 15)
    elif voltage >= 3.00: percent = int(2  + (voltage - 3.00) / 0.40 * 8)
    else:                 percent = 0

    percent = max(0, min(100, percent))
    print(f"BAT raw={int(raw)} voltage={voltage:.2f}V percent={percent}%")
    return percent

# === Initialisation BLE ===
ble = BLERadio()
uart = UARTService()
battery_service = BatteryService()
advertisement = ProvideServicesAdvertisement(uart, battery_service)
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

# === Initialisation batterie ===
battery_service.level = read_battery_percent()
last_battery_update = time.monotonic()

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
                    print(f"BLE sent: {msg}")
                except Exception as e:
                    print("BLE Error:", e)
            else:
                print(msg)
        event_buffer = []
        last_flush = now

    time.sleep(0.005)

    if now - last_battery_update >= 60:
        battery_service.level = read_battery_percent()
        last_battery_update = now
