from gi.repository import Gtk, GObject
from xtreme_shell.modules.utils import Blp


@Blp("quick-button")
class QuickButton(Gtk.Button):
    __gtype_name__ = "QuickButton"

    text: Gtk.Label = Gtk.Template.Child()
    subtitle: Gtk.Label = Gtk.Template.Child()
    icon: Gtk.Image = Gtk.Template.Child()

    @GObject.Property(type=str)
    def btt_label(self):
        return self.text.get_label()

    @btt_label.setter
    def btt_label(self, text):
        self.text.set_label(text)

    @GObject.Property(type=str)
    def btt_icon_name(self):
        return self.icon.get_icon_name()

    @btt_icon_name.setter
    def btt_icon_name(self, icon):
        self.icon.set_from_icon_name(icon)

    def __init__(self):
        super().__init__()


class ButtonService(GObject.Object):
    widget: QuickButton
    locked = GObject.Property(type=bool, default=False)

    def __init__(self, button):
        super().__init__()
        self.__active = False
        self.widget = button

        button.connect("clicked", self.on_clicked)

    def on_clicked(self, _):
        self.active = not self.active

    def bind_lock(self, prop, object, func=None, invert=False):
        def on_change(*_):
            val = getattr(object.props, prop, None) is not None
            self.locked = val if not invert else not val

        cb = on_change if not func else func
        object.connect(f"notify::{prop}", cb)
        cb()

    @GObject.Property(type=bool, default=False)
    def active(self):
        return self.__active

    @active.setter
    def active(self, value):
        if self.locked is False:
            self.__active = value
            self.notify("active")
            self.widget.add_css_class(
                "active"
            ) if value else self.widget.remove_css_class("active")
