import threading
from library.yaml_manager import YamlManager
from library.serial_manager import SerialManager
from library.ui_manager import UIManager
from library.macro_manager import MacroManager
from library.log_manager import init_log

DEBUG = True

def main():
    init_log()
    yaml_manager = YamlManager(debug=DEBUG)
    macro_manager = MacroManager(yaml_manager, debug=DEBUG)
    serial_manager = SerialManager(yaml_manager, macro_manager, debug=DEBUG)
    ui_manager = UIManager(yaml_manager, serial_manager)

    serial_thread = threading.Thread(
        target=serial_manager.listen_loop,
        daemon=True
    )
    serial_thread.start()

    ui_manager.run()


if __name__ == "__main__":
    main()
