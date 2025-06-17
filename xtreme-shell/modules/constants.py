from pathlib import Path

LOG_DIR = Path.home() / ".local" / "state" / "xtreme-shell"


# Creation of paths
LOG_DIR.mkdir(parents=True, exist_ok=True)
