from modules.constants import LOG_DIR
from rich.logging import RichHandler
from gi.repository import GLib
from pathlib import Path
import logging


def init_logger():
    log_file: Path = LOG_DIR / "shell-logs.txt"
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(name)s] [%(levelname)s] [%(funcName)s] %(message)s",
        handlers=[
            RichHandler(rich_tracebacks=True),
            logging.FileHandler(str(log_file)),
        ],
    )

    log_file.open("a").write(
        f"\n{'-' * 10} {GLib.DateTime.new_now_local().format('%I:%M %p %b %Y')} {'-' * 10}"
    )
