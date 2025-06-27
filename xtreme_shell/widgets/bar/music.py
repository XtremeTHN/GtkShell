from gi.repository import AstalMpris, Gtk, GLib, Pango, GObject
from xtreme_shell.modules.config import BarMusic
from xtreme_shell.widgets.box import Box
from xtreme_shell.widgets.cava import Cava
import logging


def to_minutes(seconds):
    seconds = int(seconds)
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


class BlurryImage(Gtk.Picture):
    def __init__(self, blur: int | float = 0, **kwargs):
        super().__init__(**kwargs)
        self.__blur = blur

    @GObject.Property
    def blur(self):
        return self.__blur

    @blur.setter
    def blur(self, blur):
        self.__blur = blur
        self.notify("blur")

    def do_snapshot(self, snapshot):
        snapshot.push_blur(self.blur)
        Gtk.Picture.do_snapshot(self, snapshot)
        snapshot.pop()


class MusicPopover(Gtk.Popover):
    player: AstalMpris.Player = GObject.Property(type=AstalMpris.Player)

    def __init__(self):
        super().__init__(has_arrow=False, width_request=350, height_request=150)
        self.set_offset(0, 10)
        frame = Gtk.Frame.new()
        overlay = Gtk.Overlay.new()

        self.background = BlurryImage(
            blur=20,
            content_fit=Gtk.ContentFit.COVER,
        )

        self.cava = Cava()
        self.cava.set_css("color: colors.$tertiary")

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

        BarMusic.blur.bind(self.background, "blur")
        BarMusic.opacity.bind(self.opacity_box, "opacity")
        self.bind_property(
            "visible", self.cava, "visible", flags=GObject.BindingFlags.SYNC_CREATE
        )

        frame.set_child(overlay)
        self.set_child(frame)

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

    def set_player(self, player):
        self.player = player
        self.player.connect("notify::playback-status", self.__update_playback_status)
        self.player.connect("notify::available", self.__toggle_cava)
        self.__toggle_cava()
        self.__update_playback_status()

    def __toggle_cava(self, *_):
        self.cava.set_active(self.player.get_available())

    def __update_playback_status(self, *_):
        if self.player.get_playback_status() == AstalMpris.PlaybackStatus.PLAYING:
            self.play_button.set_icon_name("media-playback-pause-symbolic")
        elif self.player.get_playback_status() == AstalMpris.PlaybackStatus.PAUSED:
            self.play_button.set_icon_name("media-playback-start-symbolic")

    def update(self):
        self.background.set_filename(self.player.get_cover_art())
        self.title.set_label(self.player.get_title())
        self.artist.set_label(self.player.get_artist())


class MusicLabel(Gtk.Overlay):
    def __init__(self):
        super().__init__(css_classes=["clickable"])
        gesture = Gtk.GestureClick.new()
        self.add_controller(gesture)

        self.ids = []
        self.logger = logging.getLogger("MusicLabel")
        self.player = None
        self.popover = MusicPopover()
        self.popover.set_parent(self)

        self.background = BlurryImage(
            css_classes=["bar-container"],
            content_fit=Gtk.ContentFit.COVER,
            vexpand=False,
            hexpand=False,
        )

        self.label = Gtk.Label(margin_start=5, margin_end=5)
        self.opacity_box = Box(hexpand=True, vexpand=True)
        self.opacity_box.set_css(
            "border-radius: 4px; background-color: colors.$surface-container"
        )

        BarMusic.blur.bind(self.background, "blur")
        BarMusic.opacity.bind(self.opacity_box, "opacity")
        BarMusic.player.on_change(self.__set_player, once=True)

        gesture.connect("released", self.__popup)

        self.add_overlay(self.background)
        self.add_overlay(self.opacity_box)
        self.add_overlay(self.label)

        self.set_measure_overlay(self.label, True)

    def __popup(self, *_):
        self.popover.popup()

    def __change_visible(self, *_):
        if self.player.get_available() is False:
            self.set_visible(False)
            self.label.set_text("")
        else:
            self.set_visible(True)

    def __set_player(self, name):
        self.logger.info(f"Changing player to {name}...")
        self.player = AstalMpris.Player.new(name)
        self.popover.set_player(self.player)

        self.player.connect("notify::available", self.__change_visible)
        self.player.connect("notify", self.__update)

    def __update(self, *_):
        self.__change_visible()
        self.popover.update()
        if (a := self.player.get_cover_art()) not in ["", None]:
            self.background.set_filename(a)

        GLib.idle_add(
            self.label.set_text,
            f"{self.player.get_title() or 'Unkown song'} {to_minutes(self.player.props.position)} / {to_minutes(self.player.props.length)}",
        )
