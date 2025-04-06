from gi.repository import Gtk

from lib.logger import getLogger
from lib.services.backlight import Backlight, Adapter


class BacklightSlider(Gtk.Scale):
    def __init__(self):
        self.adj = Gtk.Adjustment(lower=0, upper=1, step_increment=0.1)
        super().__init__(css_classes=["quickslider"], hexpand=True, adjustment=self.adj, orientation=Gtk.Orientation.HORIZONTAL)
        self.logger = getLogger("BacklightSlider")

        self.backlight: Backlight = Backlight.get_default()
        self.adapter: Adapter = None
        self.__adapter_id = 0

        self.backlight.connect("notify::adapter", self.__on_change); self.__on_change()
        self.connect("value-changed", self.__on_value_change); self.__on_value_change()

    def __on_change(self, *_):
        self.adapter = self.backlight.adapter
        if self.adapter is None:
            self.logger.warning("Adapter is None. Hiding...")
            self.set_visible(False)
        else:
            self.set_visible(True)
            self.set_value(self.adapter.value / self.adapter.max_brightness)

    def __on_value_change(self, *_):
        val = self.adj.get_value()
        self.adapter.value = val * self.adapter.max_brightness
        if val < 0.04:
            self.remove_css_class("upper")
            self.add_css_class("lower")
        else:
            self.remove_css_class("lower")
            self.add_css_class("upper")
