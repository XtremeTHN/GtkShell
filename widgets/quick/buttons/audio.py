from gi.repository import AstalWp, Gtk
from widgets.custom.buttons import QuickButton
from widgets.quick.menus.audio import QuickMixerMenu

class QuickMixer(QuickButton):
    def __init__(self):
        self.icon = Gtk.Image(icon_name="audio-volume-medium-symbolic", pixel_size=24)
        super().__init__(icon=self.icon, header="Mixer", default_subtitle="No applications")

        self.wp = AstalWp.get_default().get_audio()
        self.set_menu(QuickMixerMenu(), "mixer", "Mixer")

        self.wp.connect("notify::streams", self.__on_streams_change)

    def __on_streams_change(self, *_):
        if len(self.wp.props.streams) == 0:
            self.subtitle.set_text("No applications")
            self.set_active(False)
            return
        else:
            self.subtitle.set_text(f"{len(self.wp.props.streams)} applications")
            self.set_active(True)