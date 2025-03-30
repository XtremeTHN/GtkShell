from gi.repository import Gtk, AstalNetwork

from widgets.quick.menus.network import QuickNetworkMenu
from widgets.quick.icons import NetworkIndicator
from widgets.custom.buttons import QuickButton


class QuickNetwork(QuickButton):
    def __init__(self):
        self.net_icon = NetworkIndicator(size=24, bind_ssid=False)
        self.wrapper = self.net_icon.net
        super().__init__(icon=self.net_icon, header="Internet", default_subtitle="Connected")
        self.wrapper.net.connect("notify::state", self.__change_subtitle); self.__change_subtitle()
        self.wrapper.connect("notify::ssid", self.__change_title); self.__change_title()

        self.button.connect("clicked", self.toggle)

        self.set_menu(QuickNetworkMenu(), "network", "Network", max_size=150)

        self.connect("activated", self.on_activate)
        self.connect("deactivated", self.on_deactivate)
        
    def on_activate(self, _):
        if self.wrapper.is_wifi() is True:
            self.wrapper.wifi.set_enabled(True)
            
    def on_deactivate(self, _):
        if self.wrapper.is_wifi() is True:
            self.wrapper.wifi.set_enabled(False)

    def toggle(self, *_):
        self.set_active(not self.active)
    
    def __change_title(self, *_, force=False):
        if force is True or self.wrapper.is_wired() or self.wrapper.ssid is None:
            self.heading.set_label("Internet")
        else:
            self.heading.set_label(self.wrapper.ssid)

    def __change_subtitle(self, *_):
        match self.wrapper.net.get_state():
            case AstalNetwork.State.DISCONNECTING:
                self.subtitle.set_label("Disconnecting...")
            case AstalNetwork.State.DISCONNECTED:
                self.subtitle.set_label("Disconnected")
                self.__change_title(force=True)
                self.set_active(False)
            case AstalNetwork.State.CONNECTED_GLOBAL:
                self.subtitle.set_label("Connected")
                self.__change_title()
                self.set_active(True)
            case AstalNetwork.State.CONNECTING | AstalNetwork.State.CONNECTED_SITE | AstalNetwork.State.CONNECTED_LOCAL:
                self.subtitle.set_label("Connecting...")
            case _:
                self.subtitle.set_label(f"Unknown state")

class QuickMixer(QuickButton):
    def __init__(self):
        self.icon = Gtk.Image(icon_name="audio-volume-medium-symbolic", pixel_size=24)
        super().__init__(icon=self.icon, header="Mixer", default_subtitle="No applications")