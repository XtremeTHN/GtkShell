from gi.repository import Gtk, AstalWp, GObject


def to_percentage(_, value):
    return f"{int(value * 100)}%"


class AudioIcon(Gtk.Image):
    __gtype_name__ = "AudioIcon"

    def __init__(self, size=16):
        super().__init__(pixel_size=size)

        self.audio = AstalWp.get_default()

        if not self.audio:
            print("couldn't get wayplumber instance")
            return

        self.audio.connect("notify::default-speaker", self.on_speaker_change)
        self.on_speaker_change()

    def on_speaker_change(self, *_):
        speaker = self.audio.get_default_speaker()

        if speaker is None:
            self.set_from_icon_name("audio-volume-muted-symbolic")
            return

        speaker.bind_property(
            "volume",
            self,
            "tooltip-text",
            GObject.BindingFlags.SYNC_CREATE,
            transform_to=to_percentage,
        )

        speaker.bind_property(
            "volume-icon", self, "icon-name", GObject.BindingFlags.SYNC_CREATE
        )
