from gi.repository import Gtk, Adw, Astal, GObject
from lib.network import NWrapper
from lib.utils import Box

from gi.repository.AstalNetwork import AccessPoint

class Background(Astal.Window):
    def __init__(self):
        super().__init__(namespace="astal-background", css_classes=["background"],\
                         anchor=Astal.WindowAnchor.TOP | Astal.WindowAnchor.RIGHT | Astal.WindowAnchor.BOTTOM | Astal.WindowAnchor.LEFT,\
                         layer=Astal.Layer.TOP, opacity=0.4)

class Spinner(Box):
    def __init__(self, size=14, description=None):
        super().__init__(vertical=True, spacing=10)
        self.desc = Gtk.Label.new(description)
        self.spinner = Adw.Spinner.new()
        self.spinner.props.width_request = size
        self.spinner.props.height_request = size
        self.append_all([self.desc, self.spinner])

class PasswordPage(Box):
    __gsignals__ = {
        "next-page": (GObject.SIGNAL_RUN_FIRST, None, (str,)),
    }
    def __init__(self, ap: AccessPoint):
        super().__init__(vertical=True, spacing=10)

        desc = Gtk.Label.new("Provide a password for %s" % ap.get_ssid())
        self.password = Gtk.PasswordEntry.new()
        self.password.connect('activate', self.__next_page)

        self.append_all([desc, self.password])
    
    def __next_page(self, _):
        self.emit("next-page", self.password.get_text())

class NetworkPromptNavigator(Gtk.Stack):
    def __init__(self, access_point: AccessPoint):
        super().__init__()

        _pass = PasswordPage(access_point)
        _pass.connect("next-page", self.__on_next_page)

        loading = Spinner(size=24,description="Connecting to %s" % access_point.get_ssid())

        self.add_child(_pass)
        self.add_named(loading, "loading")
    
    def __on_next_page(self, _, password):
        print(password)
        self.set_visible_child_name("loading")

class NetworkPrompt(Astal.Window):
    def __init__(self, access_point: AccessPoint):
        super().__init__(exclusivity=Astal.Exclusivity.NORMAL, keymode=Astal.Keymode.ON_DEMAND,\
                         css_classes=["network-prompt", "background"])
        
        self.background = Background()
        self.background.present()
        
        content = Box(vertical=True, spacing=20, valign=Gtk.Align.CENTER)

        title = Gtk.Label(label="Network", css_classes=["title-1"])
        nav = NetworkPromptNavigator(access_point)
        cancel_btt = Gtk.Button(label="Cancel", valign=Gtk.Align.CENTER)
        cancel_btt.connect("clicked", lambda *_: self.close())

        content.append_all([title, nav, cancel_btt])

        self.set_child(content)
        self.present()
    
    def close(self):
        super().close()
        self.background.close()