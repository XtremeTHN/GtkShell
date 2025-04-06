import pathlib

CONFIG_DIR = pathlib.Path.home() / ".config/shell"
JSON_CONFIG_PATH = CONFIG_DIR / "config.json"

__source = __file__.split("/")
try:
    SOURCE_DIR = pathlib.Path("/".join(__source[:__source.index("GtkShell") +
                                                1]))
except Exception as e:
    print("Couldn't get SOURCE_DIR. Info:", e.__class__.__name__, e.args)
    exit(1)
