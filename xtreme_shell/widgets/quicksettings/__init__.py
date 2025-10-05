from xtreme_shell.modules.utils import Blp
from gi.repository import Gtk, Adw, GLib, GObject, Astal


@Blp("quick-button")
class QuickButton(Gtk.ToggleButton):
    __gtype_name__ = "QuickButton"

    text: Gtk.Label = Gtk.Template.Child()

    @GObject.Property(type=str)
    def btt_label(self):
        return self.text.get_label()

    @btt_label.setter
    def btt_label(self, text):
        self.text.set_label(text)

    def __init__(self):
        super().__init__()


@Blp("quick-menu")
class QuickMenu(Gtk.Revealer):
    __gtype_name__ = "QuickMenu"

    icon: Gtk.Image = Gtk.Template.Child()
    root_box: Gtk.Image = Gtk.Template.Child()
    title_label: Gtk.Label = Gtk.Template.Child()

    @GObject.Property(type=str, nick="icon-name")
    def icon_name(self):
        return self.icon.get_icon_name()

    @icon_name.setter
    def icon_name(self, icon):
        self.icon.set_from_icon_name(icon)

    @GObject.Property(type=str)
    def title(self):
        return self.title_label.get_label()

    @title.setter
    def title(self, title):
        self.title_label.set_label(title)

    @GObject.Property(type=Gtk.Widget)
    def content(self):
        return

    @content.setter
    def content(self, content):
        self.root_box.append(content)

    def __init__(self):
        super().__init__()


@Blp("quick-settings")
class QuickSettings(Astal.Window):
    __gtype_name__ = "QuickSettings"

    def __init__(self):
        super().__init__(
            name="quick-settings",
            namespace="shell-quick-ssettings",
            layer=Astal.Layer.OVERLAY,
            resizable=False,
        )

        self.add_css_class("quicksettings")
        self.present()
        # self.set_visible(False)
