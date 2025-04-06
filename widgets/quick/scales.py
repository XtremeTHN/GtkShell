from gi.repository import Gtk

from lib.logger import getLogger
from lib.services.backlight import Backlight, Adapter


class QuickScale(Gtk.Overlay):

    def __init__(self,
                 lower: int,
                 upper: int,
                 step_increment=0.1,
                 icon: str | Gtk.Widget = None,
                 icon_size=16,
                 _class=[]):
        super().__init__()
        self.scale = Gtk.Scale(css_classes=["quickslider", *_class],
                               adjustment=Gtk.Adjustment(
                                   lower=lower,
                                   upper=upper,
                                   step_increment=step_increment),
                               hexpand=True,
                               orientation=Gtk.Orientation.HORIZONTAL)
        self.icon = icon

        self.set_icon(icon, size=icon_size)
        self.set_child(self.scale)

    def set_icon(self, icon: str | Gtk.Widget, size=16):
        if icon is None:
            return

        if self.icon is not None:
            self.remove_overlay(self.icon)

        if isinstance(icon, Gtk.Widget) is True:
            self.icon = icon
        else:
            self.icon = Gtk.Image.new_from_icon_name(icon)

        if "quickslider-icon" not in self.icon.get_css_classes():
            print('adding')
            #self.icon.add_css_class("quickslider-icon")

        self.icon.set_pixel_size(size)
        self.icon.set_halign(Gtk.Align.START)
        self.icon.set_margin_start(10)

        self.add_overlay(self.icon)

    def get_value(self):
        return self.scale.get_value()

    def set_value(self, val):
        self.scale.set_value(val)

    def __on_value_change(self, _):
        if self.icon is None:
            print("is none")
            return


class BacklightIcon(Gtk.Image):

    def __init__(self, adjustment):
        super().__init__(icon_name="display-brightness-symbolic",
                         css_classes=["quickslider-icon"],
                         sensitive=False)

        self.adj = adjustment
        self.adj.connect("notify::value", self.__on_value_change)

    def __on_value_change(self, *_):
        val = self.adj.get_value()
        if val < 0.04:
            self.remove_css_class("upper")
            self.add_css_class("lower")
        else:
            self.remove_css_class("lower")
            self.add_css_class("upper")

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
            self.set_value(self.adapter.value / self.adapter.max_brightness)

    def __on_value_change(self, *_):
        self.adapter.value = self.get_value() * self.adapter.max_brightness
