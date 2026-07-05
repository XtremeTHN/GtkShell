from gi.repository import Gtk, Astal, GLib, Pango, GObject, Adw

from xtreme_shell.modules.utils import Blp, to_button
from xtreme_shell.modules.niri import NiriEventStream, NiriSocket

from .tray import Tray
from .audio import AudioPopover
from .center import Center
from .music import Background

from ..icons.network import NetworkIcon
from ..icons.audio import AudioIcon
import logging


class Workspaces(Gtk.Box):
    __gtype_name__ = "Workspaces"

    def __init__(self, workspaces: int = 5):
        super().__init__()

        self.niri = NiriSocket.get_default()
        self.niri_events = NiriEventStream.get_default()

        self.widgets = []
        self.max_workspaces = workspaces

        self.setup_widgets()

    def wk(self, id):
        def on_focus_change(_, __, lbl):
            lbl.set_opacity(
                1
                if (wkspc := self.niri_events.focused_workspace) is not None
                and wkspc["id"] == lbl.id
                else 0.5
            )

        wkspc = Gtk.Label(label=str(id))
        wkspc.id = id

        on_focus_change(None, None, wkspc)
        self.niri_events.connect("notify::focused-workspace", on_focus_change, wkspc)
        self.append(wkspc)

    def setup_widgets(self):
        for x in range(1, self.max_workspaces + 1):
            self.wk(x)


class ActiveWindow(Gtk.Label):
    __gtype_name__ = "ActiveWindow"

    def __init__(self):
        super().__init__()

        self.logger = logging.getLogger("Bar")
        self.niri_events = NiriEventStream.get_default()

        self.niri_events.bind_property(
            "focused-window",
            self,
            "label",
            transform_to=lambda _, v: "NixOS" if v is None else v.get("title", "NixOS"),
        )


@Blp("bar")
class Bar(Astal.Window):
    __gtype_name__ = "Bar"

    ovr: Gtk.Overlay = Gtk.Template.Child()
    clock: Gtk.Label = Gtk.Template.Child()
    audio: AudioIcon = Gtk.Template.Child()
    center_box: Gtk.CenterBox = Gtk.Template.Child()

    def __init__(self):
        super().__init__(
            name="bar",
            namespace="shell-bar",
            anchor=Astal.WindowAnchor.TOP,
            width_request=800,
        )

        self.logger = logging.getLogger("Bar")
        self.niri_events = NiriEventStream.get_default()
        self.niri_events.connect("overview-changed", self.overview_changed)

        self.setup_anim()
        self.setup_widgets()

        self.add_css_class("adwaita-window-no-shadow")
        self.present()

    def is_anim_idle(self):
        return all(
            [
                self.show_anim.props.state != Adw.AnimationState.PLAYING,
                self.hide_anim.props.state != Adw.AnimationState.PLAYING,
            ]
        )

    def overview_changed(self, _, is_opened: bool):
        if is_opened:
            self.show_anim.reset()
            self.show_anim.play()
        else:
            self.hide_anim.reset()
            self.hide_anim.play()

    def update_time(self, clock):
        clock.set_label(GLib.DateTime.new_now_local().format("%I:%M %p %a %b %Y"))
        return True

    def on_anim(self, value):
        self.set_margin_top(value)

    def setup_anim(self):
        self.target_hide = Adw.CallbackAnimationTarget.new(self.on_anim)
        self.target_show = Adw.CallbackAnimationTarget.new(self.on_anim)

        self.hide_anim = Adw.TimedAnimation.new(
            self, 0, -self.get_height() - 10, 400, self.target_hide
        )
        self.show_anim = Adw.TimedAnimation.new(
            self, -self.get_height() + 10, 0, 400, self.target_show
        )

        self.hide_anim.set_easing(Adw.Easing.EASE_OUT_QUAD)
        self.show_anim.set_easing(Adw.Easing.EASE_OUT_QUAD)

    def setup_widgets(self):
        self.audio_popover = AudioPopover()
        self.center = Center()

        GLib.timeout_add_seconds(1, self.update_time, self.clock)

        to_button(
            self.clock, lambda _: self.center.set_visible(not self.center.get_visible())
        )

        GLib.timeout_add_seconds(2, self.setup_anim)

        self.audio_popover.set_parent(self.audio)
        to_button(self.audio, lambda _: self.audio_popover.popup())

        self.ovr.set_measure_overlay(self.center_box, True)
