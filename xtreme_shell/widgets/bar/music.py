from gi.repository import AstalMpris, Gtk, Pango
from xtreme_shell.lib.config import Config
from xtreme_shell.lib.logger import getLogger
from xtreme_shell.widgets.custom.box import Box, ColoredBox
from xtreme_shell.widgets.custom.icons import BlurryImage


def to_minutes(seconds):
    seconds = int(seconds)
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


class MusicPopover(Gtk.Popover):
    def __init__(self, player=None):
        super().__init__(has_arrow=False)
        self.player = None
        self.__signal_id = 0
        self.conf = Config.get_default().bar.music
        self.set_player(player)

        self.set_size_request(350, 150)
        self.set_offset(0, 8)

        overlay = Gtk.Overlay()
        self.background = BlurryImage(
            blur=20,
            content_fit=Gtk.ContentFit.COVER, vexpand=False, hexpand=False
        )
        frame = Gtk.Frame(child=self.background)
        transparency = ColoredBox("rgba(colors.$background, 0.8)")
        transparency.set_background_opt(self.conf.transparency)
        overlay.add_overlay(frame)
        overlay.add_overlay(transparency)

        content = Box(
            vertical=True,
            spacing=10,
            valign=Gtk.Align.CENTER,
            halign=Gtk.Align.CENTER,
        )

        info = Box(vertical=True, spacing=0)
        self.title = Gtk.Label(
            css_classes=["title-2"],
            ellipsize=Pango.EllipsizeMode.MIDDLE,
            max_width_chars=25,
        )
        self.artist = Gtk.Label()
        info.append_all([self.title, self.artist])

        controllers = Box(spacing=10, halign=Gtk.Align.CENTER)
        self.play_button = self._create_button(
            "media-playback-start-symbolic", "Play", self.__toggle
        )
        prev_button = self._create_button(
            "media-skip-backward-symbolic", "Previous", self.__prev
        )
        next_button = self._create_button(
            "media-skip-forward-symbolic", "Next", self.__next
        )
        controllers.append_all([prev_button, self.play_button, next_button])

        content.append_all([info, controllers])
        overlay.add_overlay(content)

        self.set_child(overlay)

    def __toggle(self, _):
        if self.player:
            self.player.play_pause()

    def __next(self, _):
        if self.player:
            self.player.next()

    def __prev(self, _):
        if self.player:
            self.player.previous()

    @staticmethod
    def _create_button(icon_name, tooltip_text, function):
        btt = Gtk.Button(icon_name=icon_name, tooltip_text=tooltip_text)
        btt.connect("clicked", function)
        return btt

    def set_player(self, player):
        if self.player:
            self.player.disconnect(self.__signal_id)

        self.player: AstalMpris.Player = player
        if not self.player:
            return

        self.__signal_id = self.player.connect(
            "notify::playback-status", self.__update_playback_status
        )
        self.__update_playback_status(None, None)

    def update_info(self):
        if not self.get_visible():
            return

        self.background.set_filename(self.player.props.cover_art)
        self.title.set_label(self.player.get_title())
        self.artist.set_label(self.player.get_artist())

    def __update_playback_status(self, _, __):
        if self.player.get_playback_status() == AstalMpris.PlaybackStatus.PLAYING:
            self.play_button.set_icon_name("media-playback-pause-symbolic")
        elif self.player.get_playback_status() == AstalMpris.PlaybackStatus.PAUSED:
            self.play_button.set_icon_name("media-playback-start-symbolic")


class Music(Gtk.Label):
    def __init__(self, _class=[]):
        super().__init__(css_classes=_class)
        controller = Gtk.GestureClick.new()
        self.add_controller(controller)

        self.popover = MusicPopover()
        self.popover.set_parent(self)

        self.config = Config.get_default().bar.music
        self.logger = getLogger("Music")

        self._config_player = self.config.player.value
        self.config.player.on_change(self.__change_player)

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
        self._config_player = self.config.player.value
        self.logger.info("Changing player to %s...", self._config_player)
        self.player = AstalMpris.Player.new(self._config_player)
        self.popover.set_player(self.player)
