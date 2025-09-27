from gi.repository import Adw, Gtk, AstalMpris, GObject, Gio, AstalWp
from ..cava import Cava

import logging
import re

Player = AstalMpris.Player


class ActiveMusic(Adw.Bin):
    __gtype_name__ = "ActiveMusic"

    def __init__(self):
        super().__init__()

        self.rev = Gtk.Revealer(transition_type=Gtk.RevealerTransitionType.SWING_RIGHT)
        self.label = Gtk.Label(label="No music")

        self.player = AstalMpris.Player.new("spotify")

        self.player.connect("notify::available", self.on_available)
        self.rev.set_child(self.label)
        self.set_child(self.rev)

        self.on_available()

    def on_available(self, *_):
        self.rev.set_reveal_child(self.player.get_available())
        self.label.set_label(self.player.get_title())


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
