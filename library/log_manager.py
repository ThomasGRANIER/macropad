import datetime

class typeLog:
    info = "INFO"
    debug = "DEBUG"
    warning = "WARNING"
    error = "ERROR"

def print_log(type: str, content: str) -> None:
    timestamp = datetime.datetime.now()
    content_traited = content.replace('\n','')
    print(f"[{type}] {timestamp} : {content_traited}")
