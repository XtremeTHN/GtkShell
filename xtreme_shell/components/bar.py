from gi.repository import Gtk, Astal, AstalHyprland, GLib, Pango
from xtreme_shell.widgets.window import XtremeWindow
from xtreme_shell.modules.config import Bar as BarConfig
from xtreme_shell.widgets.box import Box

class HyprProp(Gtk.Label):
    def __init__(self, prop: str, func, **kwargs):
        super().__init__(css_classes=["bar-container"], **kwargs)
        hypr = AstalHyprland.Hyprland.get_default()
        hypr.connect(f"notify::{prop}", func)
        func(hypr)
    

class HyprWorkspaces(HyprProp):
    def __init__(self):
        super().__init__("focused-workspace", self.__on_workspace)

    def __on_workspace(self, hypr, *_):
        self.set_label(f"Workspace {hypr.props.focused_workspace.get_id()}")


class HyprWindow(HyprProp):
    def __init__(self):
        super().__init__(
            "focused-client", 
            self.__on_client,
            max_width_chars=30,
            ellipsize=Pango.EllipsizeMode.END)

    def __on_client(self, hypr, *_):
        if hypr.props.focused_client is None:
            self.set_label("NixOS")
            return
        self.set_label(f"{hypr.props.focused_client.get_title()}")


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
        date = DateTime()

        end_box.append(date)

        content.set_start_widget(left_box)
        content.set_end_widget(end_box)

        self.set_child(content)

    @staticmethod
    def is_enabled():
        return True  # TODO: change this
