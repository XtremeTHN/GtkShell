from xtreme_shell.modules.gobject import BlpTemplate
from xtreme_shell.modules.config import Bar as BarConfig
from xtreme_shell.widgets.music.current import MusicLabel
from gi.repository import Gtk, Astal, AstalHyprland, GObject, GLib
from xtreme_shell.widgets import Widget

a = Astal.WindowAnchor


@BlpTemplate("bar")
class Bar(Astal.Window):
    __gtype_name__ = "Bar"

    center_box = Gtk.Template.Child()
    start_box = Gtk.Template.Child()
    hypr_workspaces = Gtk.Template.Child()
    hypr_window = Gtk.Template.Child()
    end_box: Gtk.Box = Gtk.Template.Child()
    date_time = Gtk.Template.Child()

    def __init__(self):
        super().__init__(anchor=a.TOP | a.LEFT | a.RIGHT)

        hypr = AstalHyprland.get_default()
        hypr.bind_property(
            "focused-workspace",
            self.hypr_workspaces,
            "label",
            GObject.BindingFlags.SYNC_CREATE,
            transform_to=lambda _, x: f"Workspace {x.props.id}",
        )

        hypr.bind_property(
            "focused-client",
            self.hypr_window,
            "label",
            GObject.BindingFlags.SYNC_CREATE,
            transform_to=lambda _, x: str(
                BarConfig.fallback_title.value if not x else x.props.title
            ),
        )

        music = MusicLabel()
        self.center_box.set_center_widget(music)

        GLib.timeout_add_seconds(1, self.__update_datetime)

        Widget.set_opacity_option(self, BarConfig.opacity)

        self.present()

    def __update_datetime(self):
        time = GLib.DateTime.new_now_local().format(BarConfig.date_format.value)
        self.date_time.set_label(f"{time}")

    @staticmethod
    def is_enabled():
        return True
