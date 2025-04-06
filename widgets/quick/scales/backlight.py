from gi.repository import Gtk
from lib.services.backlight import Backlight, Adapter
from lib.logger import getLogger

from widgets.quick.scales.quick import QuickScale


class BacklightIcon(Gtk.Image):

    def __init__(self, adjustment):
        super().__init__(
            icon_name="display-brightness-symbolic",
            css_classes=["quickslider-icon"],
        )

        self.adj = adjustment
        self.adj.connect("notify::value", self.__on_value_change)

    def __on_value_change(self, *_):
        val = self.adj.get_value()

        if val >= 0.8:
            self.set_from_icon_name("display-brightness-high-symbolic")
        elif val > 0.4:
            self.set_from_icon_name("display-brightness-medium-symbolic")
        else:
            self.set_from_icon_name("display-brightness-low-symbolic")


class BacklightSlider(QuickScale):

    def __init__(self):
        super().__init__(0, 1)
        self.logger = getLogger("BacklightSlider")
        self.backlight: Backlight = Backlight.get_default()
        self.adapter: Adapter = None
        self.__adapter_id = 0

        icon = BacklightIcon(self.scale.get_adjustment())
        self.set_icon(icon)

        self.backlight.connect("notify::adapter", self.__on_change)
        self.scale.connect("value-changed", self.__on_value_change)

        self.__on_change()

    def __on_change(self, *_):
        self.adapter = self.backlight.adapter
        if self.adapter is None:
            self.logger.warning("Adapter is None. Hiding...")
            self.set_visible(False)
        else:
            self.set_visible(True)
            self.adapter.connect("notify::value", self.__on_back_changed)

    def __on_back_changed(self, *_):
        self.set_value(self.adapter.value / self.adapter.max_brightness)

    def __on_value_change(self, *_):
        self.adapter.set_value(self.get_value() * self.adapter.max_brightness)
