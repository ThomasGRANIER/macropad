import os
from pathlib import Path
import yaml
import subprocess

from library.log_manager import print_log, typeLog

class YamlManager:
    def __init__(self, config_file: str="macropad_config.yml", profile: int=1, debug: bool=False):
        self.config_file = config_file
        self.profile = profile
        self.debug = debug
        self.config = {}
        self.load_config()

    # -------------------------
    # CONFIG
    # -------------------------

    def load_config(self) -> None:
        print_log(typeLog.info, f"Lecture de la configuration")
        if not os.path.exists(self.config_file):
            self.config = {}
        with open(self.config_file, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
            if self.debug:
                for item, val in self.config.items():
                    print_log(typeLog.debug, f"{item}:{val}")

    def save_config(self) -> None:
        if self.debug:
            print_log(typeLog.info, f"Sauvegarde de la configuration : {self.config}")
        with open(self.config_file, "w", encoding="utf-8") as f:
            yaml.dump(self.config, f)

    def get_serial_port(self) -> str:
        port = self.config["serial_port"]
        if self.debug:
            print_log(typeLog.debug, f"Récupération du port : {port}")
        return port

    def get_grid_size(self) -> tuple[str,str]:
        nb_ligne=self.config["nb_ligne"]
        nb_column=self.config["nb_column"]
        if self.debug:
            print_log(typeLog.debug, f"Récupération de la taille de la grille : nb ligne={nb_ligne}, nb colonne={nb_column}")
        return nb_ligne,nb_column

    # -------------------------
    # MACROS
    # -------------------------

    def open_editor(self, file: str) -> None:
        file_path = Path(f"profiles/{self.profile}/{file}.yml")
        print_log(typeLog.info, f"Ouverture du fichier {file_path} dans l'editeur")

        if not file_path.exists():
            file_path.touch()

        subprocess.Popen(["gio","open", file_path])

    def load_yaml_file(self, file_path) -> dict:
        if self.debug:
            print_log(typeLog.debug, f"Lecture du yaml {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get_macro_name(self, pos: str, max_chars_per_line: int=15) -> str:
        if self.debug:
            print_log(typeLog.debug, f"Récupération du nom de la macro {pos}")
        filename = f"profiles/{self.profile}/{pos}.yml"
        if not os.path.exists(filename):
            return ""

        try:
            data = self.load_yaml_file(filename) or {}
            name = data.get("name", "").strip()

            if not name:
                return ""

            words = name.split(" ")
            lines = []
            current_line = ""

            for word in words:
                # Si on peut ajouter le mot à la ligne actuelle
                if len(current_line) + len(word) + (1 if current_line else 0) <= max_chars_per_line:
                    if current_line:
                        current_line += " "
                    current_line += word
                else:
                    # Sinon, on ferme la ligne et commence une nouvelle
                    if current_line:
                        lines.append(current_line)
                    current_line = word

            if current_line:
                lines.append(current_line)

            wrapped_name = "\n".join(lines)

            if self.debug:
                print_log(typeLog.debug, f"Nom récupéré (avec retour à la ligne propre) : {wrapped_name}")
            return wrapped_name

        except Exception:
            return ""

    def get_macro_actions(self, key_name) -> dict:
        if self.debug:
            print_log(typeLog.debug, f"Checher fichier lié à la {key_name} reçu")
        filename = f"profiles/{self.profile}/{key_name}.yml"
        if not os.path.exists(filename):
            return None
        return self.load_yaml_file(filename)
