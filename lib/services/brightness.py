from lib.utils import Watcher, GObject, Object
from lib.logger import getLogger
from os.path import join
import os

DISPLAYS_FOLDER = "/sys/class/backlight/"

class Adapter(Watcher):
    def __init__(self, display):
        super().__init__()
        self.logger = getLogger(f"Adapter ({display})")

        self.__max_brightness = 0
        self.__value = 0

        self.__path = join(DISPLAYS_FOLDER, display)
        self.__max_path = join(self.__path, "max_brightness")
        self.__curr_path = join(self.__path, "brightness")
        self.add_watch(self.__max_path)
        self.add_watch(self.__curr_path)

    @GObject.Property(type=int, nick="max-brightness", flags=GObject.PARAM_READABLE)
    def max_brightness(self):
        return self.__max_brightness

    @GObject.Property(type=int)
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if isinstance(value, int) is False:
            raise ValueError("Expected int")

        try:
            f = open(self.__max_path, "w")
        except PermissionError:
            self.logger.error("Need permissions for changing brightness. Install the udev rule")
            return

        try:
            f.write(str(value))
        except:
            self.logger.exception("Error while setting brightness")
        finally:
            f.close()
    

class Brightness(Watcher):

    def __init__(self):
        super().__init__()
        self.logger = getLogger("Brightness")
        self.__adapters = []
        self.__adapter = None
        self.__update_adapters()

        if len(adapters) == 0:
            self.logger.warning("No adapters available")

        self.add_watch(DISPLAYS_FOLDER)
        self.connect("event", self.__on_change)

    @GObject.Property(flags=GObject.ParamFlags.READABLE)
    def adapters(self):
        return self.__adapters

    @GObject.Property(flags=GObject.ParamFlags.READABLE)
    def adapter(self):
        return self.__adapter

    def __update_adapters(self):
        self.__adapters = [Adapter(x[1]) for x in os.walk(DISPLAYS_FOLDER)]
        self.__adapter = __self.adapters[0]

        self.notify("adapters")
        self.notify("adapter")

    def __on_change(self, event):
        self.logger.debug("Updating adapters...")
        self.__update_adapters()
