from gi.repository import Gtk, GObject, AstalWp
from ..icons.audio import AudioIcon
from xtreme_shell.modules.utils import box
import logging


class AudioPopover(Gtk.Popover):
    def __init__(self):
        super().__init__(width_request=200)
        self.logging = logging.getLogger("AudioPopover")
        self._speaker = None

        wp = AstalWp.get_default()
        if not wp:
            self.logging.error("Could'nt get wayplumber instance")
            return

        self.audio = wp.get_audio()
        self.audio.bind_property(
            "default-speaker", self, "speaker", GObject.BindingFlags.SYNC_CREATE
        )

        self.slider = Gtk.Scale.new_with_range(
            orientation=Gtk.Orientation.HORIZONTAL, min=0, max=100, step=1
        )
        self.slider.set_hexpand(True)
        self.slider.set_draw_value(False)

        self.slider.connect("value-changed", self.on_volume_changed)

        self.set_child(self.slider)

    @GObject.Property(type=AstalWp.Endpoint)
    def speaker(self):
        return self._speaker

    @speaker.setter
    def speaker(self, value):
        self._speaker = value
        value.connect("notify::volume", self.on_volume_notify)

    def on_volume_notify(self, *_):
        self.slider.set_value(self.speaker.get_volume() * 100)

    def on_volume_changed(self, _):
        value = self.slider.get_value() / 100

        if self.speaker is None:
            self.logging.error("Could'nt get default speaker")
            return

        self.speaker.set_volume(value)
