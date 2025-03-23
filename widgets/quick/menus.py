from gi.repository import Gtk, Adw, AstalNetwork
from lib.network import NWrapper
from widgets.prompts.network import NetworkPrompt
from lib.utils import Box

class StatusPage(Box):
    def __init__(self, title=None, description=None, icon=None):
        super().__init__(vertical=True, vexpand=True, valign=Gtk.Align.CENTER)
        self.__title = Gtk.Label(label=title, css_classes=["title-3"])
        self.__description = Gtk.Label(label=description, css_classes=["dimmed"])
        self.__icon = Gtk.Image(icon_name=icon, pixel_size=28)

        self.append_all([self.__icon, self.__title, self.__description])
    
    def set_title(self, title):
        self.__title.set_label(title)
    
    def set_description(self, desc):
        self.__description.set_label(desc)
    
    def set_icon_name(self, icon_name):
        self.__icon.set_from_icon_name(icon_name)

class WifiButton(Gtk.Button):
    def __init__(self, access_point: AstalNetwork.AccessPoint, active_ssid: str):
        super().__init__()
        self.ap = access_point
        self.content = Box(spacing=10, hexpand=True)
        self.icon = Gtk.Image(pixel_size=16,icon_name=access_point.get_icon_name())
        self.name = Gtk.Label(label=access_point.get_ssid(), hexpand=True, xalign=0)

        self.content.append_all([self.icon, self.name])

        if active_ssid == access_point.get_ssid():
            self._connected = Gtk.Image(icon_name="emblem-ok-symbolic", pixel_size=16, \
                                        halign=Gtk.Align.END, visible=active_ssid == access_point.get_ssid())
            self.content.append(self._connected)
            self.add_css_class("active-wifi")

        self.set_child(self.content)
        self.connect("clicked", self.__on_clicked)
    
    def __on_clicked(self, _):
        p = NetworkPrompt(self.ap)
        p.present()

# TODO: Refactor this class to use Gtk.ListView for using Adw.ClampScrollable
# See: https://discourse.gnome.org/t/gtk4-gtk-listview-python-example/12323/5
class QuickNetworkMenu(Box):
    def __init__(self):
        super().__init__(css_classes=["quick-network-menu"], vertical=True, spacing=4)
        self.wrapper = NWrapper.get_default()

        self.placeholder = StatusPage()
        
        self.wrapper.connect("changed", self.__on_wrapper_change); self.__on_wrapper_change(None)
        self.connect("notify::children", self.__on_children_change); self.__on_children_change(None)

        self.append(self.placeholder)

    def __on_children_change(self, *_):
        if len(self.children) == 1:
            print("showing place")
            self.show_zero_wifi_placeholder()
        else:
            self.placeholder.set_visible(False)

    def __on_wrapper_change(self, _):
        if self.wrapper.is_wired():
            self.show_no_wifi_device_placeholder()
        else:
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
    
    def show_no_wifi_device_placeholder(self):
        self.placeholder.set_title("No wifi device")
        self.placeholder.set_description("No wifi devices available. Connect a wifi dongle")
        self.placeholder.set_icon_name("network-wireless-disabled-symbolic")
        self.placeholder.set_visible(True)