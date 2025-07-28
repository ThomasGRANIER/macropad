import subprocess
import sys

if len(sys.argv) > 1:
    text = sys.argv[1]
    print(text)
    subprocess.run(["xdotool", "type", text])
else:
    print("Missing argument")
    sys.exit(1)
