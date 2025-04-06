from widgets.custom.buttons import QuickUtilButton
from widgets.custom.box import QuickMenu, Box
from lib.logger import getLogger

from gi.repository import AstalWp, Gtk, Pango


class AppMixer(Box):

    def __init__(self, stream: AstalWp.Endpoint):
        super().__init__(vertical=True,
                         valign=Gtk.Align.START,
                         hexpand=True,
                         css_classes=["false-button", "box-10"])
        self.stream = stream

        app_box = Box(spacing=10, halign=Gtk.Align.CENTER)
        icon = Gtk.Image(icon_name=stream.get_icon(), pixel_size=24)
        label = Gtk.Label(label=stream.get_name(),
                          wrap=True,
                          ellipsize=Pango.EllipsizeMode.MIDDLE)

        app_box.append_all([icon, label])

        self.slider = Gtk.Scale.new(
            Gtk.Orientation.HORIZONTAL,
            Gtk.Adjustment(lower=0, upper=1, step_increment=0.1))

        self.slider.connect("value-changed", self.__on_scale_change)
        self.stream.connect("notify::volume", self.__on_volume_change)
        self.__on_volume_change(None, None)

        self.append_all([app_box, self.slider])

    def __on_scale_change(self, _):
        self.stream.set_volume(self.slider.get_value())

    def __on_volume_change(self, _, __):
        self.slider.set_value(self.stream.get_volume())

class QuickMixerMenu(QuickMenu):

    def __init__(self):
        super().__init__("Mixer", 250, logger_name="QuickMixerMenu")
        self.audio = AstalWp.get_default().get_audio()
        self.__streams = {}

        self.set_placeholder_attrs("No applications",
                                   "Open an application to use the mixer",
                                   "audio-volume-medium-symbolic")

        self.audio.connect("stream-added", self.__on_stream_added)
        self.audio.connect("stream-removed", self.__on_stream_removed)

    def __on_stream_added(self, _, stream):
        w = AppMixer(stream)
        self.logger.debug(f"Added stream with id {stream.get_id()} to mixer")
        self.__streams[stream.get_id()] = w
        self.append(w)

    def __on_stream_removed(self, _, stream):
        id = stream.get_id()
        self.logger.debug(f"Added stream with id {id} to mixer")
        self.remove(self.__streams.pop(id))


class QuickMixer(QuickUtilButton):

    def __init__(self):
        self.icon = Gtk.Image(icon_name="audio-volume-medium-symbolic",
                              pixel_size=24)
        wp = AstalWp.get_default().get_audio()
        super().__init__(icon=self.icon, header="Mixer", default_subtitle="No applications", \
                         object=wp, watch_property="streams")

        self.set_menu(QuickMixerMenu(), "mixer")
