from gi.repository import Adw, Gtk, AstalMpris, GObject, Gio, AstalWp

from ..circular_progress import CircularProgress
from ..cava import Cava

import logging
import re

Player = AstalMpris.Player


class ActiveMusic(Adw.Bin):
    __gtype_name__ = "ActiveMusic"

    def __init__(self):
        super().__init__()

        self.rev = Gtk.Revealer(transition_type=Gtk.RevealerTransitionType.SWING_RIGHT)

        box = Gtk.Box(spacing=10)

        img = Gtk.Image.new()
        self.prog = CircularProgress()
        self.prog.widget = img
        img.set_from_paintable(self.prog)
        img.set_margin_start(4)
        img.set_margin_top(2)
        img.set_margin_bottom(2)

        self.label = Gtk.Label(label="No music")

        box.append(img)
        box.append(self.label)

        self.player = AstalMpris.Player.new("spotify")

        self.player.bind_property(
            "title", self.label, "label", GObject.BindingFlags.SYNC_CREATE
        )
        self.player.bind_property(
            "available", self.rev, "reveal-child", GObject.BindingFlags.SYNC_CREATE
        )
        self.player.bind_property(
            "position",
            self.prog,
            "progress",
            GObject.BindingFlags.SYNC_CREATE,
            lambda _, v: v / self.player.props.length
            if self.player.props.length > 0
            else 0,
        )

        self.rev.set_child(box)
        self.set_child(self.rev)


class Background(Cava):
    __gtype_name__ = "Background"

    def __init__(self):
        super().__init__()

        self.logger = logging.getLogger("BackgroundCava")

        self.blur = 20

        self.__mpris_player_id = 0
        self.__player = None
        self.mpris = AstalMpris.get_default()

        wp = AstalWp.get_default()
        if not wp:
            self.logger.warning("AstalWp returned None. No cava available")
        else:
            audio = wp.get_audio()
            audio.connect("notify::streams", self.__find_stream)

        self.__change_player("last")

    def __on_available_change(self, *_):
        self.queue_draw()

    def __find_stream(self, audio: AstalWp.Audio, _):
        name = "spotify"
        self.logger.info(f"Trying to find the stream of {name}...")
        pattern = re.compile(re.escape(name), re.IGNORECASE)

        for x in audio.get_streams():
            if pattern.search(x.get_name()) or pattern.search(x.get_description()):
                self.cava.stream = x
                self.set_visible(True)
                self.set_active(True)
                return

        self.set_visible(False)
        self.set_active(False)
        self.logger.warning("Stream not found")

    def __set_player_from_mpris(self, _, player):
        if not player:
            players = self.mpris.get_players()
            if len(players) == 0:
                self.logger.info("No player available")
                return
            else:
                player = players[-1]

        self.logger.info(f"Changing player to {player.get_bus_name()}...")
        self.__player = player
        self.__player.connect("notify::available", self.__on_available_change)
        self.__on_available_change()

    def __change_player(self, player):
        if player != "last":
            if self.__mpris_player_id != 0:
                self.mpris.disconnect(self.__mpris_player_id)

            self.logger.info(f"Changing player to {player}")
            self.__set_player_from_mpris(None, player)
        else:
            self.logger.info("Choosing the last player from the mpris list...")
            self.__mpris_player_id = self.mpris.connect(
                "player-added", self.__set_player_from_mpris
            )
            self.__set_player_from_mpris(None, None)
