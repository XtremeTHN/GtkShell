from gi.repository import Gtk
from lib.logger import getLogger


class QuickScale(Gtk.Overlay):
    def __init__(
        self,
        lower: int,
        upper: int,
        step_increment=0.1,
        vertical=False,
        icon: str | Gtk.Widget = None,
        icon_size=16,
        _class=[],
    ):
        super().__init__()
        self.scale = Gtk.Scale(
            css_classes=["quickslider", *_class],
            adjustment=Gtk.Adjustment(
                lower=lower, upper=upper, step_increment=step_increment
            ),
            hexpand=True,
            orientation=Gtk.Orientation.VERTICAL
            if vertical is True
            else Gtk.Orientation.HORIZONTAL,
        )
        self.icon = icon

        self.set_icon(icon, size=icon_size)
        self.set_child(self.scale)

        self.scale.connect("value-changed", self.__on_value_change)
        self.__on_value_change(None)

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
            self.icon.add_css_class("quickslider-icon")

        self.icon.set_pixel_size(size)
        self.icon.set_halign(Gtk.Align.START)
        self.icon.set_margin_start(10)
        self.icon.set_sensitive(False)

        self.add_overlay(self.icon)

    def get_value(self):
        return self.scale.get_value()

    def set_value(self, val):
        self.scale.set_value(val)

    def __on_value_change(self, _):
        val = self.get_value()
        if self.icon is None:
            return

        if val < 0.04:
            self.icon.remove_css_class("upper")
            self.icon.add_css_class("lower")
        else:
            self.icon.remove_css_class("lower")
            self.icon.add_css_class("upper")
