from lib.utils import Watcher, GObject, Object
from lib.logger import getLogger
from os.path import join
import os

DISPLAYS_FOLDER = "/sys/class/backlight/"

class Adapter(GObject.GObject):
    def __init__(self, display):
        super().__init__()
        self.logger = getLogger(f"Adapter ({display})")

        self.__max_brightness = 0
        self.__value = 0

        self.__path = join(DISPLAYS_FOLDER, display)
        self.__max_path = join(self.__path, "max_brightness")
        self.__curr_path = join(self.__path, "brightness")

        self.__read()

    def __read(self):
        try:
            max_bright = open(self.__max_path)
            curr_bright = open(self.__curr_path)
        except:
            self.logger.exception("Couldn't open backlight files")
        try:
            self.__max_brightness = int(max_bright.read())
            self.__value = int(curr_bright.read())
            self.notify("max-brightness")
            self.notify("value")
        except:
            self.logger.exception("Couldn't parse backlight values")

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
            f = open(self.__curr_path, "w")
        except PermissionError:
            self.logger.error("Need permissions for changing brightness. Install the udev rule")
            return

        try:
            f.write(str(value))
            f.flush()
        except:
            self.logger.exception("Error while setting brightness")
        finally:
            f.close()
    

class Backlight(Object):

    def __init__(self):
        super().__init__()
        self.logger = getLogger("Backlight")
        self.__watcher = Watcher()

        self.__adapters = []
        self.__adapter = None
        self.__update_adapters()

        if len(self.__adapters) == 0:
            self.logger.warning("No adapters available")

        self.__watcher.add_watch(DISPLAYS_FOLDER)
        self.__watcher.connect("event", self.__on_change)

    @GObject.Property(flags=GObject.ParamFlags.READABLE)
    def adapters(self):
        return self.__adapters

    @GObject.Property(flags=GObject.ParamFlags.READABLE)
    def adapter(self):
        return self.__adapter

    def __update_adapters(self):
        self.__adapters = []
        for _, files, _ in os.walk(DISPLAYS_FOLDER):
            for x in files:
                self.__adapters.append(Adapter(x))
        self.__adapter = self.__adapters[0] if len(self.__adapters) > 0 else None

        self.notify("adapters")
        self.notify("adapter")

    def __on_change(self, event):
        self.logger.debug("Updating adapters...")
        self.__update_adapters()
