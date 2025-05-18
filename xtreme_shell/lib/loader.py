import importlib.util
import os

from xtreme_shell.lib.config import Config
from xtreme_shell.lib.constants import MODULES_DIR
from xtreme_shell.lib.logger import getLogger

class ModuleLoader:
    def __init__(self):
        self.logger = getLogger("ModuleLoader")

    def load_from_config(self):
        m = Config.get_default().modules.value
        if isinstance(m, dict) is False:
            self.logger.error(
                f"Expected dictionary, got {type(m).__name__}. Refusing to load modules..."
            )
            return []
        return [self.load(x) for x in m["files"]]

    def load(self, module_name):
        path = MODULES_DIR / module_name / "main.py"
        if path.is_file() is False:
            self.logger.warning("%s does not exists or it's not a file", module_name)
            return
        return self.load_from_path(path)

    def load_from_path(self, path):
        if os.path.exists(path):
            self.logger.info(f"Loading script from '{path}'...")

            spec = importlib.util.spec_from_file_location("module", path)
            if spec is None:
                self.logger.error("Failed to load script. spec is None")
                return
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "init") is False:
                self.logger.warning(f"{path} does not have init method. Skipping...")
                return

            return module
        else:
            self.logger.error(f"File '{path}' doesn't exists")
