from gi.repository import Gtk

from lib.logger import getLogger
from lib.services.backlight import Backlight, Adapter

class BacklightSlider(Gtk.Scrollbar):
    def __init__(self):
        self.adj = Gtk.Adjustment(lower=0, upper=1, step_increment=0.1)
        super().__init__(hexpand=True, adjustment=self.adj, orientation=Gtk.Orientation.HORIZONTAL)
        self.logger = getLogger("BacklightSlider")

        self.backlight: Backlight = Backlight.get_default()
        self.adapter: Adapter = None
        self.__adapter_id = 0

        self.backlight.connect("notify::adapter", self.__on_change); self.__on_change()
        self.adj.connect("notify::value", self.__on_value_change)

    def __on_change(self, *_):
        self.adapter = self.backlight.adapter
        if self.adapter is None:
            self.logger.warning("Adapter is None. Hiding...")
            self.set_visible(False)
        else:
            self.set_visible(True)
            self.adj.set_value(self.adapter.value / self.adapter.max_brightness)

    def __on_value_change(self, *_):
        self.adapter.value = self.adj.get_value() * self.adapter.max_brightness
