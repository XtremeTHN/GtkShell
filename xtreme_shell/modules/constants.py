from pathlib import Path

LOG_DIR = Path.home() / ".local" / "state" / "xtreme-shell"
CONFIG_DIR = Path.home() / ".config" / "xtreme-shell"

# Creation of paths
LOG_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
