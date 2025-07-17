import sys
import time
import platform
import yaml

is_windows = platform.system() == "Windows"

if is_windows:
    import keyboard
else:
    import subprocess

# Vérifie qu'un argument a bien été fourni
if len(sys.argv) > 1:
    script = sys.argv[1]

    with open(script, 'r') as f:
        data = yaml.safe_load(f)

    #print("Nom du script :", data.get("name"))

    print(data.get("notification"))

    for i, action in enumerate(data.get("actions", []), start=1):
        action_type = action.get("type")
        value = action.get("value")
        #print(f"Action {i}:")
        #print(f"  Type: {action_type}")
        #print(f"  Valeur: {value}")

        # Tu peux traiter les types comme ceci :
        if action_type == "key":
            #print(f"    => Appuyer sur : {value}")
            if is_windows:
                keyboard.press_and_release(value)
            else:
                subprocess.run(["xdotool", "key", value])

        elif action_type == "delay":
            #print(f"    => Attendre {value} ms")
            time.sleep(value / 1000)
        elif action_type == "keyboard":
            #print(f"    => Taper le texte : {value}")
            if is_windows:
                keyboard.write(value)
            else:
                subprocess.run(["xdotool", "type", value])
        elif action_type == "cmd":
            #print(f"    => Lancer la commande : {value}")
            subprocess.Popen(value, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

