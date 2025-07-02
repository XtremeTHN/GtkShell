from gi.repository import AstalMpris, AstalWp, GObject, Pango, Gtk
from xtreme_shell.modules.config import Music, MusicCava
from xtreme_shell.widgets.window import XtremeWindow
from xtreme_shell.widgets.images import BlurryImage
from xtreme_shell.widgets.cava import Cava
from xtreme_shell.widgets.box import Box

import logging


class MusicViewer(XtremeWindow):
    player: AstalMpris.Player = GObject.Property(type=AstalMpris.Player)

    def __init__(self):
        super().__init__(
            "music",
            "music",
            "overlay",
            ["bottom", "right"],
            css_classes=["music"],
            width_request=280,
            height_request=350,
            margin_end=10,
            margin_bottom=10,
        )

        frame = Gtk.Frame.new()
        overlay = Gtk.Overlay.new()

        self.player = AstalMpris.Player.new("spotify")
        self.logger = logging.getLogger("MusicViewer")
        self.wp = AstalWp.get_default()
        self.audio = self.wp.get_audio()

        self.background = BlurryImage(
            blur=20,
            content_fit=Gtk.ContentFit.COVER,
        )

        self.cava = Cava()
        self.cava.set_css("color: colors.$secondary")

        self.opacity_box = Box(hexpand=True, vexpand=True)
        self.opacity_box.set_css("background-color: colors.$surface-container")

        controls = self.__create_box(vertical=True, spacing=10)
        label_box = self.__create_box(vertical=True)

        self.title = Gtk.Label(
            css_classes=["title-1"],
            max_width_chars=45,
            justify=Gtk.Justification.CENTER,
            ellipsize=Pango.EllipsizeMode.MIDDLE,
        )
        self.artist = Gtk.Label(css_classes=["title-4"])

        label_box.append(self.title, self.artist)

        button_box = self.__create_box(spacing=5)

        previous = self.__create_button("media-skip-backward-symbolic", self.__prev)
        self.play_button = self.__create_button(
            "media-playback-start-symbolic", self.__play_pause
        )
        next = self.__create_button("media-skip-forward-symbolic", self.__next)

        button_box.append(previous, self.play_button, next)

        controls.append(label_box, button_box)

        overlay.add_overlay(self.background)
        overlay.add_overlay(self.cava)
        overlay.add_overlay(self.opacity_box)
        overlay.add_overlay(controls)

        Music.background_blur.bind(self.background, "blur")
        Music.opacity.bind(self.opacity_box, "opacity")

        MusicCava.bind_all(self.cava.cava, exclude=["blur", "enabled"])
        MusicCava.blur.bind(self.cava, "blur")

        self.bind_property(
            "visible", self.cava, "visible", flags=GObject.BindingFlags.SYNC_CREATE
        )

        self.audio.connect("notify::streams", self.__find_stream)

        self.update()

        frame.set_child(overlay)
        self.set_child(frame)

        self.present()

        self.set_player(self.player)

        self.player.bind_property(
            "available",
            self,
            "visible",
            flags=GObject.BindingFlags.SYNC_CREATE,
        )
        self.player.connect("notify", lambda *_: self.update())

    def __create_box(self, **kwargs):
        return Box(halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER, **kwargs)

    def __create_button(self, icon, func):
        b = Gtk.Button(icon_name=icon)
        b.connect("clicked", func)
        return b

    def __prev(self, _):
        self.player.previous()

    def __play_pause(self, _):
        self.player.play_pause()

    def __next(self, _):
        self.player.next()

    def __find_stream(self, *_):
        name = self.player.get_bus_name().split(".")[-1]

        if self.audio is None:
            self.logger.warning("No audio")
            return

        stream = None
        for x in self.audio.get_streams():
            if x.get_name().lower() == name.lower():
                stream = x
                break

        if not stream:
            return

        self.cava.set_stream(stream)

    def set_player(self, player):
        self.player = player
        self.player.connect("notify::playback-status", self.__update_playback_status)
        self.player.connect("notify::available", self.__on_available_changed)
        self.__on_available_changed()
        self.__update_playback_status()

    def __on_available_changed(self, *_):
        self.cava.set_active(self.player.get_available())

    def __update_playback_status(self, *_):
        if self.player.get_playback_status() == AstalMpris.PlaybackStatus.PLAYING:
            self.play_button.set_icon_name("media-playback-pause-symbolic")
        elif self.player.get_playback_status() == AstalMpris.PlaybackStatus.PAUSED:
            self.play_button.set_icon_name("media-playback-start-symbolic")

    def update(self):
        self.background.set_filename(self.player.get_cover_art())
        self.title.set_label(self.player.get_title() or "Unknown song")
        self.artist.set_label(self.player.get_artist() or "Unknown artist")

    @staticmethod
    def is_enabled():
        return Music.enabled.value
