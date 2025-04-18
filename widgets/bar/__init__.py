from widgets.custom.icons import NetworkIndicator, VolumeIndicator, BatteryIndicator
from widgets.custom.widget import CustomizableWidget
from widgets.bar.hypr import Workspace, ActiveWindow
from widgets.bar.music import Music
from widgets.custom.box import Box

from gi.repository import Gtk, Astal, GLib
from lib.config import Config

class BarContent(Gtk.CenterBox, CustomizableWidget):
    def __init__(self):
        Gtk.CenterBox.__init__(self, css_classes=["bar"], orientation=Gtk.Orientation.HORIZONTAL)
        CustomizableWidget.__init__(self)
        self.conf = Config.get_default()
        self.background_opacity = self.conf.bar.background_opacity
        self._setup_widgets()
        self._connect_signals()

    def _setup_widgets(self):
        # Left side
        self.left_box = Box(spacing=10)
        self.workspaces = Workspace(_class=["bar-container"])
        self.active_window = ActiveWindow(_class=["bar-container"])
        self.left_box.append_all([self.workspaces, self.active_window])

        # Right side
        self.right_box = Box(spacing=10)

        self.music = Music(_class=["bar-container"])
        self.date_widget = Gtk.Label(css_classes=["bar-container"])

        self.quickicons = Box(spacing=10, css_classes=["bar-container"])
        self.network_indicator = NetworkIndicator()
        self.volume_indicator = VolumeIndicator()
        self.battery_indicator = BatteryIndicator()

        self.quickicons.append_all([
            self.network_indicator, self.volume_indicator,
            self.battery_indicator
        ])
        self.right_box.append_all(
            [self.music, self.date_widget, self.quickicons])

        self.set_start_widget(self.left_box)
        self.set_end_widget(self.right_box)

    def _connect_signals(self):
        GLib.timeout_add(1000, self.__update_date)
        self.conf.bar.background_opacity.on_change(self.change_opacity, once=True)

    def __update_date(self, *_):
        GLib.idle_add(self.date_widget.set_label,
                      GLib.DateTime.new_now_local().format("%I:%M %p %b %Y"))
        return True


class Bar(Astal.Window):

    def __init__(self, m):
        super().__init__(gdkmonitor=m,
                         namespace="astal-topbar",
                         css_classes=["bar-window"],
                         anchor=Astal.WindowAnchor.TOP
                         | Astal.WindowAnchor.LEFT | Astal.WindowAnchor.RIGHT,
                         exclusivity=Astal.Exclusivity.EXCLUSIVE)
        self.set_child(BarContent())

        self.present()
