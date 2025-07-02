from xtreme_shell.widgets.images import BlurryImage
from gi.repository import AstalMpris, Gtk, GLib
from xtreme_shell.modules.config import Music
from xtreme_shell.widgets.box import Box
from xtreme_shell.widgets import Widget
import logging


def to_minutes(seconds):
    seconds = int(seconds)
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


class MusicLabel(Gtk.Overlay):
    def __init__(self):
        super().__init__(css_classes=["clickable"])

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
        self.opacity_box = Box(hexpand=True, vexpand=True)
        Widget.set_css(
            self.opacity_box,
            "border-radius: 4px; background-color: colors.$surface-container",
        )

        Music.background_blur.bind(self.background, "blur")
        Music.opacity.bind(self.opacity_box, "opacity")
        Music.player.on_change(self.__set_player, once=True)

        self.add_overlay(self.background)
        self.add_overlay(self.opacity_box)
        self.add_overlay(self.label)

        self.set_measure_overlay(self.label, True)

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

        self.__change_visible()

    def __update(self, *_):
        self.__change_visible()
        if (a := self.player.get_cover_art()) not in ["", None]:
            self.background.set_filename(a)

        GLib.idle_add(
            self.label.set_text,
            f"{self.player.get_title() or 'Unkown song'} {to_minutes(self.player.props.position)} / {to_minutes(self.player.props.length)}",
        )
