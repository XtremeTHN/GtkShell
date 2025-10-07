from xtreme_shell.modules.utils import Blp

from xtreme_shell.widgets.icons.network import Network
from gi.repository import Gtk, GObject, Astal

from .button import QuickButton
from .network import NetManager
from .bluetooth import BluetoothManager


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

    power_btt: Gtk.Button = Gtk.Template.Child()
    power_menu: QuickMenu = Gtk.Template.Child()

    audio_scale: Gtk.Scale = Gtk.Template.Child()
    brightness_scale: Gtk.Scale = Gtk.Template.Child()

    network_btt: QuickButton = Gtk.Template.Child()
    bluetooth_btt: QuickButton = Gtk.Template.Child()

    connections_menu: QuickMenu = Gtk.Template.Child()

    power_mode_btt: QuickButton = Gtk.Template.Child()
    night_light_btt: QuickButton = Gtk.Template.Child()

    profile_menu: QuickMenu = Gtk.Template.Child()

    def __init__(self):
        super().__init__(
            name="quick-settings",
            namespace="shell-quick-ssettings",
            layer=Astal.Layer.OVERLAY,
            resizable=False,
        )

        BluetoothManager(self.bluetooth_btt)
        NetManager(self.network_btt)

        self.add_css_class("quicksettings")
        self.present()
        # self.set_visible(False)
