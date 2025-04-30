from gi.repository import AstalMpris, Gtk

from lib.config import Config
from lib.logger import getLogger
from widgets.custom.box import Box


def to_minutes(seconds):
    seconds = int(seconds)
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


class MusicPopover(Gtk.Popover):
    def __init__(self, player=None):
        super().__init__(has_arrow=False)
        self.player = player
        self.set_size_request(350, 150)
        self.set_offset(0, 8)

        ovrl = Gtk.Overlay()
        self.background = Gtk.Picture(
            content_fit=Gtk.ContentFit.COVER, vexpand=False, hexpand=False
        )
        frame = Gtk.Frame(child=self.background)
        transparency = Box(css_classes=["music-popover-content"])
        ovrl.set_child(Box())

        content = Box(
            vertical=True,
            spacing=10,
            valign=Gtk.Align.CENTER,
            halign=Gtk.Align.CENTER,
        )

        info = Box(vertical=True, spacing=0)
        self.title = Gtk.Label(css_classes=["title-2"])
        self.artist = Gtk.Label()
        info.append_all([self.title, self.artist])

        controllers = Box(spacing=10, halign=Gtk.Align.CENTER)
        play_btt = Gtk.Button(
            icon_name="media-playback-start-symbolic", tooltip_text="Play"
        )
        prev_btt = Gtk.Button(
            icon_name="media-skip-backward-symbolic", tooltip_text="Previous"
        )
        next_btt = Gtk.Button(
            icon_name="media-skip-forward-symbolic", tooltip_text="Next"
        )
        controllers.append_all([prev_btt, play_btt, next_btt])

        content.append_all([info, controllers])
        ovrl.add_overlay(frame)
        ovrl.add_overlay(transparency)
        ovrl.add_overlay(content)

        self.set_child(ovrl)

    def set_player(self, player):
        self.player: AstalMpris.Player = player

    def update_info(self):
        if self.get_visible() is False:
            return

        self.background.set_filename(self.player.props.cover_art)
        self.title.set_label(self.player.get_title())
        self.artist.set_label(self.player.get_artist())


# CONECTANDO COSAS
class Music(Gtk.Label):
    def __init__(self, _class=[]):
        super().__init__(css_classes=_class)
        controller = Gtk.GestureClick.new()
        self.add_controller(controller)

        self.popover = MusicPopover()
        self.popover.set_parent(self)

        self.config: Config = Config.get_default()
        self.logger = getLogger("Music")

        self._config_player = self.config.bar.music_player.value
        self.config.bar.music_player.on_change(self.__change_player)

        self.player = AstalMpris.Player.new(self._config_player)
        self.popover.set_player(self.player)
        self.__change_visible(None, None)
        self.player.connect("notify::available", self.__change_visible)
        self.player.connect("notify", self.__update_info)
        controller.connect("released", self.__on_click)

    def __on_click(self, *_):
        self.popover.popup()

    def __update_info(self, _, __):
        self.set_text(
            f"{self.player.get_title()} - {to_minutes(self.player.get_position())} / {to_minutes(self.player.get_length())}"
        )
        self.popover.update_info()

    def __change_visible(self, _, __):
        if self.player.get_available() is False:
            self.logger.info(f"{self._config_player} disappeared")
            self.set_visible(False)
            self.set_text("")
        else:
            self.logger.info(f"{self._config_player} appeared")
            self.set_visible(True)

        return self.player.get_available()

    def __change_player(self, _):
        self._config_player = self.config.bar.music_player.value
        self.logger.info("Changing player to %s...", self._config_player)
        self.player = AstalMpris.Player.new(self._config_player)
        self.popover.set_player(self.player)
