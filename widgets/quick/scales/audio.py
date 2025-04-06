from gi.repository import Gtk, AstalWp
from lib.logger import getLogger

from widgets.custom.icons import VolumeIndicator
from widgets.quick.scales.quick import QuickScale

class AudioSlider(QuickScale):
    def __init__(self):
        super().__init__(0, 1)
        self.wp = AstalWp.get_default()
        self.logger = getLogger("AudioSlider")
        self.__speaker = None

        icon = VolumeIndicator(bind_volume=False)
        self.set_icon(icon)

        self.wp.connect("notify::default-speaker", self.__on_speaker_change)
        self.__on_speaker_change()
        self.scale.connect("value-changed", self.__on_value_change)

    def __on_speaker_change(self, *_):
        self.__speaker = self.wp.get_default_speaker()
        if self.__speaker is None:
            self.logger.warning("No speaker available. Hiding...")
            self.set_visible(False)
        else:
            self.logger.debug("Found speaker")
            self.set_visible(True)
            self.__speaker.connect("notify::volume", self.__on_vol_change)

    def __on_vol_change(self, *_):
        self.set_value(self.__speaker.get_volume())

    def __on_value_change(self, _):
        self.__speaker.set_volume(self.get_value())
