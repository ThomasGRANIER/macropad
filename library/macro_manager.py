import subprocess
import time

from library.yaml_manager import YamlManager
from library.log_manager import print_log, typeLog


class MacroManager:
    def __init__(self, yaml_manager: YamlManager, debug: bool = False):
        self.yaml_manager = yaml_manager
        self.debug = debug

    # -------------------------

    def execute_actions(self, key_name: str) -> None:
        action_config = self.yaml_manager.get_macro_actions(key_name)

        if not action_config:
            return

        action_name = action_config["name"]

        if len(action_name) > 0:
            print_log(typeLog.info, f"Exécution de la macro : {action_name}")
        else:
            print_log(typeLog.info, f"Exécution de la macro lié à {key_name}")

        for cmd in action_config.get("actions", []):
            action_type = cmd.get("type")
            value = str(cmd.get("value", ""))

            if self.debug:
                print_log(typeLog.debug, f"{key_name} : {action_type} - {value}")

            if action_type == "key":
                subprocess.run(["xdotool", "key", value])

            elif action_type == "text":
                subprocess.run(["xdotool", "type", value])

            elif action_type == "cmd":
                subprocess.Popen(
                    value,
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

            elif action_type == "delay":
                try:
                    time.sleep(int(value) / 1000)
                except Exception:
                    pass
