from xtreme_shell.widgets.music.current import MusicLabel
from xtreme_shell.modules.config import Bar as BarConfig
from xtreme_shell.widgets.window import XtremeWindow
from gi.repository import Gtk, Astal, GLib
from .wm import HyprWindow, HyprWorkspaces
from xtreme_shell.widgets.box import Box


class DateTime(Gtk.Label):
    def __init__(self):
        super().__init__(css_classes=["bar-container"])

        GLib.timeout_add(1000, self.__change_date)

    def __change_date(self):
        time = GLib.DateTime.new_now_local().format(BarConfig.date_format.value)
        self.set_label(f"{time}")


class Bar(XtremeWindow):
    def __init__(self):
        super().__init__(
            "astal-topbar",
            "topbar",
            "top",
            ["top", "left", "right"],
            exclusivity=Astal.Exclusivity.EXCLUSIVE,
        )

        self.logger.info("Initializing...")

        self.set_opacity_option(BarConfig.opacity)

        self.setup_widgets()
        self.present()

    def setup_widgets(self):
        content = Gtk.CenterBox(css_classes=["bar-box"])

        left_box = Box(spacing=10)
        workspaces = HyprWorkspaces()
        window = HyprWindow()
        left_box.append(workspaces, window)

        end_box = Box(spacing=10)
        music = MusicLabel()
        date = DateTime()

        end_box.append(music, date)

        content.set_start_widget(left_box)
        content.set_end_widget(end_box)

        self.set_child(content)

    @staticmethod
    def is_enabled():
        return BarConfig.enabled.value  # TODO: change this
