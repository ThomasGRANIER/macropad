import time
import board
import keypad
import rotaryio
from digitalio import DigitalInOut, Direction, Pull
import displayio
import adafruit_displayio_ssd1306
from adafruit_display_text import label
import terminalio
import sys

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

# === Initialisation Bluetooth ===
ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

# === Initialisation écran OLED ===
displayio.release_displays()
i2c = board.I2C()  
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C) 
WIDTH = 128
HEIGHT = 32
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)
splash = displayio.Group()
display.root_group = splash

# Texte par défaut
text_area = label.Label(terminalio.FONT, text="En attente...", x=0, y=16)
splash.append(text_area)

# === Clavier matrice ===
row_pins = (board.P0_09, board.P0_10, board.P0_02)
col_pins = (board.P1_11, board.P1_13, board.P1_15)
keys = keypad.KeyMatrix(row_pins=row_pins, column_pins=col_pins, columns_to_anodes=True)
num_cols = len(col_pins)

# === Encodeur 1 ===
# encoder1 = rotaryio.IncrementalEncoder(board.GP27, board.GP26)
# last_position1 = encoder1.position
# button1 = DigitalInOut(board.GP29)
# button1.direction = Direction.INPUT
# button1.pull = Pull.UP
# button1_last = button1.value

# === Encodeur 2 ===
encoder2 = rotaryio.IncrementalEncoder(board.P1_06, board.P1_04)
last_position2 = encoder2.position
button2 = DigitalInOut(board.P0_24)
button2.direction = Direction.INPUT
button2.pull = Pull.UP
button2_last = button2.value

# === Lancement publicité Bluetooth ===
ble.start_advertising(advertisement)

# Pour lecture série non-bloquante
import supervisor

# Tampon pour accumuler les caractères reçus
serial_buffer = ""

while True:
    if ble.connected:
        text_area.text = "Connecte"
    else:
        text_area.text = "En attente..."
        if not ble.advertising:
            ble.start_advertising(advertisement)
            
    # Lecture série (non bloquante)
    if supervisor.runtime.serial_bytes_available:
        char = sys.stdin.read(1)  # Lire un caractère
        if char == "\n" or char == "\r":
            if serial_buffer.strip():
                print(f"Reçu : {serial_buffer}")
                text_area.text = serial_buffer[:21]  # Tronque si plus large que l'écran
            serial_buffer = ""
        else:
            serial_buffer += char

    # Clavier
    event = keys.events.get()
    if event:
        row = event.key_number % num_cols + 1
        col = event.key_number // num_cols + 1
        if event.pressed:
            if ble.connected:
                msg = f"l{row}c{col}\n"
                uart.write(msg.encode("utf-8"))
            else:
                print(f"l{row}c{col}")

    # Encodeur 1 rotation
    # pos1 = encoder1.position
    # if pos1 != last_position1:
    #     direction = "-" if pos1 > last_position1 else "+"
    #     if ble.connected:
    #         msg = f"E1{direction}\n"
    #         uart.write(msg.encode("utf-8"))
    #     else:
    #         print(f"E1{direction}")
    #     last_position1 = pos1

    # Encodeur 2 rotation
    pos2 = encoder2.position
    if pos2 != last_position2:
        direction = "-" if pos2 > last_position2 else "+"
        if ble.connected:
            msg = f"E2{direction}\n"
            uart.write(msg.encode("utf-8"))
        else:
            print(f"E2{direction}")
        last_position2 = pos2

    # Bouton 1 (avec debounce simple)
    # if button1.value != button1_last:
    #     time.sleep(0.01)  # petit debounce
    #     if button1.value == False:
    #         if ble.connected:
    #             msg = f"E1B\n"
    #             uart.write(msg.encode("utf-8"))
    #         else:
    #             print("E1B")
    #     button1_last = button1.value

    # Bouton 2 (avec debounce simple)
    if button2.value != button2_last:
        time.sleep(0.01)
        if button2.value == False:
            if ble.connected:
                msg = f"E2B\n"
                uart.write(msg.encode("utf-8"))
            else:
                print("E2B")
        button2_last = button2.value

    time.sleep(0.01)
