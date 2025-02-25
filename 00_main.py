from Vlib.Startup_logging.SafeLaunch import SafeLaunch

from Vlib.Startup_logging.SafeLaunch import SafeLaunch
from main import main, stop

if __name__ == "__main__":
    mainLaucher = SafeLaunch(main, stop, log_file="main.log", log_backup_dir="/home/item/ErrorLogs")
    mainLaucher.run()
    print("mainLaucher.run() done")