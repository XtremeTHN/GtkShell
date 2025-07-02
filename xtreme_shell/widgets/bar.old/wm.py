from gi.repository import Gtk, AstalHyprland, Pango


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
            ellipsize=Pango.EllipsizeMode.END,
        )

    def __on_client(self, hypr, *_):
        if hypr.props.focused_client is None:
            self.set_label("NixOS")
            return
        self.set_label(f"{hypr.props.focused_client.get_title()}")
