from gi.repository import Gtk, Astal, AstalHyprland, GLib, Pango, GObject, Astal

from xtreme_shell.modules.utils import Blp, to_button

from .tray import Tray
from .audio import AudioPopover
from .center import Center
from .music import Background

from ..icons.network import NetworkIcon
from ..icons.audio import AudioIcon


class Workspaces(Gtk.Box):
    __gtype_name__ = "Workspaces"

    def __init__(self, workspaces: int = 5):
        super().__init__()
        self.hypr = AstalHyprland.get_default()

        self.widgets = []
        self.max_workspaces = workspaces

        self.setup_widgets()

    def wk(self, id):
        def on_focus_change(_, __, lbl):
            lbl.set_opacity(
                1 if self.hypr.get_focused_workspace().get_id() == lbl.id else 0.5
            )

        wkspc = Gtk.Label(label=str(id))
        wkspc.id = id

        on_focus_change(None, None, wkspc)
        self.hypr.connect("notify::focused-workspace", on_focus_change, wkspc)
        self.append(wkspc)

    def setup_widgets(self):
        for x in range(1, self.max_workspaces + 1):
            self.wk(x)


class ActiveWindow(Gtk.Label):
    __gtype_name__ = "ActiveWindow"

    def __init__(self):
        super().__init__()

        self.hypr = AstalHyprland.get_default()
        self.hypr.connect("notify::focused-client", self.on_focus_change)
        self.on_focus_change()

    def on_focus_change(self, *_):
        c = self.hypr.get_focused_client()

        if not c:
            self.set_label("ArchLinux")
            return

        c.bind_property(
            "title",
            self,
            "label",
            GObject.BindingFlags.SYNC_CREATE,
        )


@Blp("bar")
class Bar(Astal.Window):
    __gtype_name__ = "Bar"

    clock: Gtk.Label = Gtk.Template.Child()
    audio: AudioIcon = Gtk.Template.Child()
    center_box: Gtk.CenterBox = Gtk.Template.Child()

    def __init__(self):
        super().__init__(
            name="bar",
            namespace="shell-bar",
            exclusivity=Astal.Exclusivity.EXCLUSIVE,
            anchor=Astal.WindowAnchor.TOP,
            width_request=800,
            margin_top=10,
        )

        self.setup_widgets()

        self.add_css_class("adwaita-window-no-shadow")
        self.present()

    def update_time(self, clock):
        clock.set_label(GLib.DateTime.new_now_local().format("%I:%M %p %a %b %Y"))
        return True

    def setup_widgets(self):
        self.audio_popover = AudioPopover()
        self.center = Center()

        GLib.timeout_add_seconds(1, self.update_time, self.clock)

        to_button(
            self.clock, lambda _: self.center.set_visible(not self.center.get_visible())
        )

        self.audio_popover.set_parent(self.audio)
        to_button(self.audio, lambda _: self.audio_popover.popup())

        self.get_child().set_measure_overlay(self.center_box, True)
