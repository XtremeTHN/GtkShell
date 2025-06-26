from gi.repository import AstalMpris, Gtk, GLib
from xtreme_shell.modules.config import BarMusic
from xtreme_shell.widgets import Widget
import logging
import inspect


def to_minutes(seconds):
    seconds = int(seconds)
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


class BlurryImage(Gtk.Picture):
    def __init__(self, blur: int | float = 0, **kwargs):
        super().__init__(**kwargs)
        self.blur = blur

    def set_blur(self, blur):
        self.blur = blur

    def do_snapshot(self, snapshot):
        snapshot.push_blur(self.blur)
        Gtk.Picture.do_snapshot(self, snapshot)
        snapshot.pop()


class MusicLabel(Gtk.Overlay):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.logger = logging.getLogger("MusicLabel")
        self.player = None

        self.background = BlurryImage(
            css_classes=["bar-container"],
            content_fit=Gtk.ContentFit.COVER,
            vexpand=False,
            hexpand=False,
        )

        self.label = Gtk.Label(margin_start=5, margin_end=5)
        self.opacity_box = Gtk.Box(hexpand=True, vexpand=True)

        BarMusic.blur.on_change(lambda x: self.background.set_blur(x), once=True)
        BarMusic.opacity.on_change(self.__change_opacity, once=True)
        BarMusic.player.on_change(self.__set_player, once=True)

        self.add_overlay(self.background)
        self.add_overlay(self.opacity_box)
        self.add_overlay(self.label)

        self.set_measure_overlay(self.label, True)

    def __change_opacity(self, op):
        Widget.set_css(
            self.opacity_box,
            f"border-radius: 4px;\
            background-color: rgba(colors.$surface_container, {op});",
        )

    def __change_visible(self, *_):
        if self.player.get_available() is False:
            self.set_visible(False)
            self.label.set_text("")
        else:
            self.set_visible(True)

    def __set_player(self, name):
        self.logger.info(f"Changing player to {name}...")
        self.player = AstalMpris.Player.new(name)

        self.player.connect("notify::available", self.__change_visible)
        self.player.connect("notify", self.__update)

    def __update(self, *_):
        self.__change_visible()
        if (a := self.player.get_cover_art()) not in ["", None]:
            self.background.set_filename(a)

        GLib.idle_add(
            self.label.set_text,
            f"{self.player.get_title() or 'Unkown song'} {to_minutes(self.player.props.position)} / {to_minutes(self.player.props.length)}",
        )
