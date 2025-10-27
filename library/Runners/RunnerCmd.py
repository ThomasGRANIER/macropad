import subprocess
import sys
import platform
import pyautogui

is_windows = platform.system().lower() == 'windows'

if len(sys.argv) > 1:
    text = sys.argv[1]
    subprocess.Popen(text, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
else:
    print("Missing argument")
    sys.exit(1)
