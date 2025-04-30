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
        self._initialize_ui()

    def _initialize_ui(self):
        self.set_size_request(350, 150)
        self.set_offset(0, 8)

        overlay = Gtk.Overlay()
        self._setup_background(overlay)
        self._setup_content(overlay)

        self.set_child(overlay)

    def _setup_background(self, overlay):
        self.background = Gtk.Picture(
            content_fit=Gtk.ContentFit.COVER, vexpand=False, hexpand=False
        )
        frame = Gtk.Frame(child=self.background)
        transparency = Box(css_classes=["music-popover-content"])
        overlay.add_overlay(frame)
        overlay.add_overlay(transparency)

    def _setup_content(self, overlay):
        content = Box(
            vertical=True,
            spacing=10,
            valign=Gtk.Align.CENTER,
            halign=Gtk.Align.CENTER,
        )

        info = self._create_info_section()
        controllers = self._create_controller_section()

        content.append_all([info, controllers])
        overlay.add_overlay(content)

    def _create_info_section(self):
        info = Box(vertical=True, spacing=0)
        self.title = Gtk.Label(css_classes=["title-2"])
        self.artist = Gtk.Label()
        info.append_all([self.title, self.artist])
        return info

    def _create_controller_section(self):
        controllers = Box(spacing=10, halign=Gtk.Align.CENTER)
        play_button = self._create_button("media-playback-start-symbolic", "Play")
        prev_button = self._create_button("media-skip-backward-symbolic", "Previous")
        next_button = self._create_button("media-skip-forward-symbolic", "Next")
        controllers.append_all([prev_button, play_button, next_button])
        return controllers

    @staticmethod
    def _create_button(icon_name, tooltip_text):
        return Gtk.Button(icon_name=icon_name, tooltip_text=tooltip_text)

    def set_player(self, player):
        self.player: AstalMpris.Player = player

    def update_info(self):
        if not self.get_visible():
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
