from gi.repository import Gtk, AstalWp
from lib.utils import Box, getLogger

class AppMixer(Box):
    def __init__(self, stream: AstalWp.Endpoint):
        super().__init__(vertical=True, valign=Gtk.Align.START, hexpand=True, css_classes=["false-button", "box-10"])
        self.stream = stream
        
        app_box = Box(spacing=10, halign=Gtk.Align.CENTER)
        icon = Gtk.Image(icon_name=stream.get_icon(), pixel_size=24)
        label = Gtk.Label(label=stream.get_name())
        
        app_box.append_all([icon, label])

        self.slider = Gtk.Scale.new(Gtk.Orientation.HORIZONTAL, Gtk.Adjustment(lower=0, upper=1, step_increment=0.1))

        self.slider.connect("value-changed", self.__on_scale_change)
        self.stream.connect("notify::volume", self.__on_volume_change); self.__on_volume_change(None, None)

        self.append_all([app_box, self.slider])
    
    def __on_scale_change(self, _):
        self.stream.set_volume(self.slider.get_value())

    def __on_volume_change(self, _, __):
        self.slider.set_value(self.stream.get_volume())
    

class QuickMixerMenu(Box):
    def __init__(self):
        super().__init__(vertical=True, css_classes=["card"])
        self.audio = AstalWp.get_default().get_audio()
        self.logger = getLogger("QuickMixerMenu")
        
        self.__streams = {}

        self.audio.connect("stream-added", self.__on_stream_added)
        self.audio.connect("stream-removed", self.__on_stream_removed)
    
    def __on_stream_added(self, _, stream):
        w = AppMixer(stream)
        self.__streams[stream.get_id()] = w
        self.append(w)
    
    def __on_stream_removed(self, _, stream):
        self.remove(self.__streams.pop(stream.get_id()))