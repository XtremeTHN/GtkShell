from xtreme_shell.widgets.cava import Cava
from xtreme_shell.widgets.images import BlurryImage
from xtreme_shell.modules.gobject import BlpTemplate
from xtreme_shell.modules.config import Music, MusicViewer as MVConf, MusicViewerCava
from gi.repository import Gtk, Astal, AstalMpris, AstalWp, GObject, GLib, Gio
from xtreme_shell.widgets import Widget
import logging

C = Gtk.Template.Child
CB = Gtk.Template.Callback
Player = AstalMpris.Player
Status = AstalMpris.PlaybackStatus
a = Astal.WindowAnchor


@BlpTemplate("music-viewer-controls")
class MusicControls(Gtk.Box):
    __gtype_name__ = "Controls"

    title: Gtk.Label = C()
    artist: Gtk.Label = C()

    previous_btt: Gtk.Button = C()
    play_pause_btt: Gtk.Button = C()
    next_btt: Gtk.Button = C()

    def __init__(self):
        super().__init__()
        self.__player: Player = None

        self.set_default_texts()

    @GObject.Property()
    def player(self):
        return self.__player

    @player.setter
    def player(self, player):
        self.__player = player
        player.connect("notify::playback-status", self.__update_playback_status)
        player.connect("notify::title", self.__update_texts)

        self.__update_texts()
        self.__update_playback_status()

    def __update_texts(self, *_):
        if self.__player.props.available:
            self.title.set_label(self.__player.props.title or "Unknown song")
            self.artist.set_label(self.__player.props.artist or "Unknown artist")
        else:
            self.set_default_texts()

    def __update_playback_status(self, *_):
        match self.__player.get_playback_status():
            case Status.PLAYING:
                self.play_pause_btt.set_icon_name("media-playback-pause-symbolic")
            case _:
                self.play_pause_btt.set_icon_name("media-playback-start-symbolic")

    @CB()
    def previous_song(self, _):
        self.player.previous()

    @CB()
    def play_pause_song(self, _):
        self.player.play_pause()

    @CB()
    def next_song(self, _):
        self.player.next()

    def set_default_texts(self):
        self.title.set_label("No song")
        self.artist.set_label("Play some music")


@BlpTemplate("music-viewer")
class MusicViewer(Astal.Window):
    __gtype_name__ = "MusicViewer"

    overlay: Gtk.Overlay = C()

    def __init__(self):
        super().__init__(
            anchor=a.BOTTOM | a.RIGHT, width_request=280, height_request=350
        )
        self.__player: Player = None
        self.logger = logging.getLogger("MusicViewer")

        background = BlurryImage(content_fit=Gtk.ContentFit.COVER)
        self.cava = Cava()
        opacity_box = Gtk.Box(
            css_classes=["surface-container"], hexpand=True, vexpand=True
        )
        self.controls = MusicControls()

        Music.background_blur.bind(background, "blur")
        Music.opacity.bind(opacity_box, "opacity")
        Music.player.bind(self, "player", transform_to=lambda _, x: Player.new(x))

        MusicViewerCava.blur.bind(self.cava, "blur")
        MusicViewerCava.bind_all(self.cava.cava)

        self.bind_property(
            "player", self.controls, "player", GObject.BindingFlags.SYNC_CREATE
        )

        self.__player.bind_property(
            "cover-art",
            background,
            "file",
            GObject.BindingFlags.SYNC_CREATE,
            lambda _, x: Gio.File.new_for_path(x) if x else None,
        )

        self.__player.connect("notify::available", self.__on_available_change)

        self.overlay.add_overlay(background)
        self.overlay.add_overlay(self.cava)
        self.overlay.add_overlay(opacity_box)
        self.overlay.add_overlay(self.controls)

        self.present()

        wp = AstalWp.get_default()
        if not wp:
            self.logger.warning("AstalWp returned None. No cava available")
        else:
            audio = wp.get_audio()
            audio.connect("notify::streams", self.__find_stream)

    def __on_available_change(self, *_):
        avail = self.__player.get_available()
        self.set_visible(avail)
        self.cava.set_active(avail)
        self.controls.set_default_texts()

    def __find_stream(self, audio, _):
        name = self.__player.get_bus_name().split(".")[-1]

        for x in audio.get_streams():
            if x.get_name().lower() == name.lower():
                self.cava.set_stream(x)
                break

    @GObject.Property()
    def player(self):
        return self.__player

    @player.setter
    def player(self, player):
        self.__player = player

    @staticmethod
    def is_enabled():
        return MVConf.enabled.value
