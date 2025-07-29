import subprocess
import sys
import platform
import pyautogui

is_windows = platform.system().lower() == 'windows'

if len(sys.argv) > 1:
    text = sys.argv[1]
    print(text)
    if is_windows:
        pyautogui.write(text)
    else:   
        subprocess.run(["xdotool", "type", text])
else:
    print("Missing argument")
    sys.exit(1)
