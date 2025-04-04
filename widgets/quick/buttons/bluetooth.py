from gi.repository import AstalBluetooth, Gtk, GObject, Adw # type: ignore

from widgets.custom.icons import BluetoothIndicator
from widgets.custom.buttons import QuickButton
from widgets.custom.box import QuickMenu, Box

from lib.config import Config
from lib.utils import notify

class QuickBluetoothDevice(Gtk.Button):
    def __init__(self, device: AstalBluetooth.Device):
        super().__init__()
        self.device = device
        self.content = Box(spacing=10)

        icon = Gtk.Image.new_from_icon_name(device.get_icon())
        name = Gtk.Label.new(device.get_name())

        print(device.get_name(), device.get_icon())
        self.content.append_all([icon, name])

        if device.get_connected() is True:
            connected = Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
            self.content.append(connected)
        
        self.set_child(self.content)

class RevealSpin(Gtk.Revealer):
    def __init__(self):
        super().__init__()
        self.__content = Box(spacing=10)
        self.spin = Adw.Spinner.new()
        self.spin.props.width_request = 14
        self.spin.props.height_request = 14

        self.text = Gtk.Label.new("Scanning...")

        self.__content.append_all([self.spin, self.text])
        self.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)
        self.set_transition_duration(200)

        self.set_child(self.__content)

class QuickBluetoothMenu(QuickMenu):
    def __init__(self):
        super().__init__("Bluetooth", logger_name="QuickBluetoothMenu")
        self.config = Config.get_default()
        self.scanning = False
        self.items = {}

        self.blue = AstalBluetooth.get_default()
        self.adapter = self.blue.get_adapter()
        self.scan_btt = Gtk.Button(icon_name="edit-find-symbolic", css_classes=["circular"], tooltip_text="Scan for devices")
        self.spinner = RevealSpin()

        self.blue.connect("notify::adapter", self.__change_adapter)
        self.blue.connect("notify::is-powered", self.__change_powered); self.__change_powered()
        self.blue.bind_property("is-powered", self.scan_btt, "sensitive", GObject.BindingFlags.SYNC_CREATE, transform_to=lambda _, x: x)

        self.__add_bulk()
        self.blue.connect("device-added", self.__on_add)
        self.blue.connect("device-removed", self.__on_remove)
        self.scan_btt.connect("clicked", self.__toggle_scan)

        self.titlebar_pack_end(self.spinner)
        self.titlebar_pack_end(self.scan_btt)
    
    def __add_bulk(self):
        for device in self.blue.get_devices():
            self.__on_add(None, device)
    
    def __on_add(self, _, device: AstalBluetooth.Device):
        if self.config.quick_blue_show_no_name is False and device.get_name() == "":
            return
        self.items[device.get_name()] = QuickBluetoothDevice(device)
        self.append(self.items[device.get_name()])
    
    def __on_remove(self, _, device: AstalBluetooth.Device):
        if device.get_name() not in self.items:
            return
        self.remove(self.items.pop(device.get_name()))

    def __change_adapter(self, *_):
        self.adapter = self.blue.get_adapter()
    
    def __toggle_scan(self, *_):
        self.scanning = not self.scanning
        if self.scanning is True:
            self.scan_btt.set_icon_name("process-stop-symbolic")
            self.adapter.start_discovery()
            self.spinner.set_reveal_child(True)
        else:
            self.scan_btt.set_icon_name("edit-find-symbolic")
            self.adapter.stop_discovery()
            self.spinner.set_reveal_child(False)
        # self.blue.get_adapter().toggle_scan()
    
    def on_children_change(self, *_):
        if len(self.content.children) == 1:
            self.set_placeholder_attrs("Bluetooth", "No bluetooth devices available. Start a scan", "bluetooth-symbolic", True)
        else:
            self.set_placeholder_visibility(False)
    
    def __show_no_adapter_placeholder(self):
        self.set_placeholder_attrs("Bluetooth", "No bluetooth adapter found", "bluetooth-disabled-symbolic", True)
    
    def __change_powered(self, *_):
        powered = self.blue.get_is_powered()
        self.scan_btt.set_sensitive(powered)
        if powered is False:
            self.__show_no_adapter_placeholder()
        else:
            self.on_children_change()

class QuickBluetooth(QuickButton):
    def __init__(self):
        super().__init__(icon=BluetoothIndicator(size=24, _hide_if_no_adapter=False), header="Bluetooth", default_subtitle="Disabled")
        self.blue = AstalBluetooth.get_default()
        self.blue.connect("notify::is-connected", self.__change_subtitle); self.__change_subtitle()
        self.blue.connect("notify::is-powered", self.__change_subtitle); self.__change_subtitle()
        self.set_menu(QuickBluetoothMenu(), "bluetooth")

    def set_active(self, active):
        adapter = self.blue.get_adapter()
        if adapter is None:
            notify("QuickBluetooth", "No bluetooth adapter found", log=True)
            return
        self.active = active
        if active is True:
            self.button.add_css_class("active")
        else:
            self.button.remove_css_class("active")
        adapter.set_powered(self.active)
    
    def __change_subtitle(self, *_):
        if self.blue.get_is_connected():
            self.subtitle.set_text("Connected")
        elif self.blue.get_is_powered() is True:
            self.subtitle.set_text("Enabled")
            self.set_active(True)
        elif self.blue.get_is_powered() is False:
            self.subtitle.set_text("Disabled")
