import datetime
import os

NAME_FOLDER = "logs"
NAME_FILE = ""

class typeLog:
    info = "INFO"
    debug = "DEBUG"
    warning = "WARNING"
    error = "ERROR"

def init_log() -> None:
    global NAME_FILE
    os.makedirs(NAME_FOLDER, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(" ","_")
    NAME_FILE = f"{NAME_FOLDER}/log_{timestamp}.log"
    open(NAME_FILE,"a").close()

def print_log(type: str, content: str) -> None:
    timestamp = datetime.datetime.now()
    content_traited = content.replace('\n','')
    line = f"[{type}] {timestamp} : {content_traited}"
    print(line)
    with open(NAME_FILE, "a") as f:
        f.write(line + "\n")
