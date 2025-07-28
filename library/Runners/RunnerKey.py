import pyautogui
import sys

if len(sys.argv) > 1:
    list_key = sys.argv[1].split(" ")
    pyautogui.hotkey(*list_key)
else:
    print("Missing argument")
    sys.exit(1)
