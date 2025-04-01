from widgets.prompts.network import NetworkPrompt
from widgets.quick.icons import NetworkIndicator
from widgets.custom.buttons import QuickButton
from widgets.custom.pages import StatusPage
from lib.utils import Box, getLogger
from lib.network import NWrapper

from gi.repository import Gtk, AstalNetwork

class WifiButton(Gtk.Button):
    def __init__(self, access_point: AstalNetwork.AccessPoint, active_ssid: str):
        super().__init__()
        self.ap = access_point
        self.content = Box(spacing=10, hexpand=True)
        self.icon = Gtk.Image(pixel_size=16,icon_name=access_point.get_icon_name())
        self.name = Gtk.Label(label=access_point.get_ssid(), hexpand=True, xalign=0)

        self.content.append_all([self.icon, self.name])

        if active_ssid == access_point.get_ssid():
            self._connected = Gtk.Image(icon_name="emblem-ok", pixel_size=16, \
                                        halign=Gtk.Align.END, visible=active_ssid == access_point.get_ssid())
            self.content.append(self._connected)
            self.add_css_class("active-wifi")

        self.set_child(self.content)
        self.connect("clicked", self.__on_clicked)
    
    def __on_clicked(self, _):
        p = NetworkPrompt(self.ap)
        p.present()

class QuickNetworkMenu(Box):
    def __init__(self):
        super().__init__(vertical=True, spacing=4)
        self.logger = getLogger("QuickNetworkMenu")
        self.wrapper = NWrapper.get_default()

        self.placeholder = StatusPage()
        self.append(self.placeholder)
        
        self.wrapper.connect("changed", self.__on_wrapper_change); self.__on_wrapper_change(None)
        self.connect("notify::children", self.__on_children_change)

    def __on_children_change(self, *_):
        if len(self.children) == 1:
            self.show_zero_wifi_placeholder()
        else:
            self.placeholder.set_visible(False)

    def __on_wrapper_change(self, _):
        if self.wrapper.is_wired():
            self.logger.info("Detected wired connection")
            self.show_wired_placeholder()
        elif self.wrapper.is_wifi() is False:
            self.logger.info("Detected no wifi device")
            self.show_no_wifi_device_placeholder()
        else:
            self.logger.info("Detected wifi device")
            self.wrapper.wifi.scan()
            self.wrapper.wifi.connect("notify::access-points", self.__on_access_points_changed); self.__on_access_points_changed()
            self.placeholder.set_visible(False)
        
    def __on_access_points_changed(self, *_):
        w = [WifiButton(a, self.wrapper.ssid) for a in self.wrapper.wifi.get_access_points() if a.get_ssid() is not None]
        self.clear()
        self.append_all(w)

    def show_zero_wifi_placeholder(self):
        self.placeholder.set_title("No wifi nearby")
        self.placeholder.set_description("No wifi devices to connect")
        self.placeholder.set_icon_name("network-wireless-no-route-symbolic")
        self.placeholder.set_visible(True)
    
    def show_wired_placeholder(self):
        self.placeholder.set_title("Wired connection")
        self.placeholder.set_description("The pc is connected to a wired network")
        self.placeholder.set_icon_name("network-wired-symbolic")
        self.placeholder.set_visible(True)
    
    def show_no_wifi_device_placeholder(self):
        self.logger.info("Showing no wifi device placeholder")
        self.placeholder.set_title("No wifi device")
        self.placeholder.set_description("Connect a wifi dongle")
        self.placeholder.set_icon_name("network-wireless-disabled-symbolic")
        self.placeholder.set_visible(True)

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
                