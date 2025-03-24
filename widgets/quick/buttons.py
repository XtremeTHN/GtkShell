from gi.repository import Gtk, AstalNetwork, Adw, GObject
from lib.utils import Box, Timeout
from widgets.quick.icons import NetworkIndicator
from widgets.quick.menus import QuickNetworkMenu

class QuickButton(Box):
    __gsignals__ = {
        "activated": (GObject.SIGNAL_RUN_FIRST, None, tuple()),
        "deactivated": (GObject.SIGNAL_RUN_FIRST, None, tuple()),
    }
    def __init__(self, icon, header, default_subtitle):
        """
        Creates a QuickButton widget.

        :param icon: A Gtk.Image widget to be used as the icon on the QuickButton.
        :type icon: Gtk.Image
        :param header: A string to be used as the header of the QuickButton.
        :type header: str
        :param default_subtitle: A string to be used as the default subtitle of the QuickButton.
        :type default_subtitle: str
        """
        super().__init__(vertical=True)

        self.active = False

        self.overlay = Gtk.Overlay.new()
        self.button = Gtk.Button(css_classes=["quickbutton"])
        self.right_button = Gtk.Button(css_classes=["quickbutton-right"], halign=Gtk.Align.END, icon_name="go-next-symbolic")

        self.button_content = Box(spacing=10)
        self._label_box = Box(spacing=0, vertical=True)
        self.heading = Gtk.Label(label=header, xalign=0, css_classes=["quickbutton-heading"])
        self.subtitle = Gtk.Label(label=default_subtitle, xalign=0, css_classes=["quickbutton-subtitle"])

        self.revealer = Gtk.Revealer(transition_type=Gtk.RevealerTransitionType.SLIDE_DOWN, transition_duration=600)

        self._label_box.append_all([self.heading, self.subtitle])
        self.button_content.append_all([icon, self._label_box])

        self.button.set_child(self.button_content)

        self.overlay.set_child(self.button)
        self.overlay.add_overlay(self.right_button)
        self.overlay.set_measure_overlay(self.right_button, True)

        self.right_button.connect("clicked", self.toggle_menu)
        
        self.append_all([self.overlay, self.revealer])
    
    def set_active(self, active):
        if active is True:
            self.active = True
            self.emit("activated")
            self.button.add_css_class("active")
        else:
            self.active = False
            self.emit("deactivated")
            if self.wrapper.is_wifi() is True:
                self.wrapper.wifi.set_enabled(False)
            self.button.remove_css_class("active")
    
    def toggle_menu(self, *_):
        """Toggles the visibility of the Revealer child. It will remove or add the class menu.
        """
        def remove():
            self.right_button.remove_css_class("menu")
            self.button.remove_css_class("menu")
        def add():
            self.button.add_css_class("menu")
            self.right_button.add_css_class("menu")

        condition = not self.revealer.get_reveal_child()
        self.revealer.set_reveal_child(condition)
        if condition is True:
            add()
        else:
            # for smooth transition
            Timeout(remove, 430)
    
    def set_menu(self, menu, max_size=100):
        """
        Sets the Gtk.Revealer widget (menu). It will reveal when you click the button with an arrow

        Args:
            menu (Gtk.Widget): The menu widget
            max_size (int, optional): The maximun size of the menu. Defaults to 100.
        """
        # m = Adw.Clamp(maximum_size=max_size, orientation=Gtk.Orientation.VERTICAL)
        # m.set_child(Gtk.ScrolledWindow(child=menu, hscrollbar_policy=Gtk.PolicyType.NEVER, max_content_height=max_size, css_classes=["n-card"]))
        self.revealer.set_child(menu)
        self.menu = menu

class QuickNetwork(QuickButton):
    def __init__(self):
        self.net_icon = NetworkIndicator(size=24, bind_ssid=False)
        self.wrapper = self.net_icon.net
        super().__init__(icon=self.net_icon, header="Internet", default_subtitle="Connected")
        self.wrapper.net.connect("notify::state", self.__change_subtitle); self.__change_subtitle()
        self.wrapper.connect("notify::ssid", self.__change_title); self.__change_title()

        self.button.connect("clicked", self.toggle)

        self.set_menu(QuickNetworkMenu(), max_size=150)

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

class QuickSysTray(QuickButton):
    def __init__(self):
        self.icon = Gtk.Image(icon_name="system-run-symbolic", pixel_size=24)
        super().__init__(icon=self.icon, header="System tray", default_subtitle="No applications")

class QuickMixer(QuickButton):
    def __init__(self):
        self.icon = Gtk.Image(icon_name="audio-volume-medium-symbolic", pixel_size=24)
        super().__init__(icon=self.icon, header="Mixer", default_subtitle="No applications")