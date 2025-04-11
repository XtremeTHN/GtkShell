from gi.repository import AstalBluetooth, Gtk, GObject, Adw  # type: ignore

from widgets.custom.icons import BluetoothIndicator
from widgets.custom.buttons import QuickButton
from widgets.custom.box import QuickMenu, Box

from lib.bluetooth import XtrBluetooth
from lib.logger import getLogger
from lib.config import Config
from lib.utils import notify


def get_name_or_address(device):
    return device.get_address() if (n := device.get_name()) in ["", None
                                                                ] else n


class RevealSpin(Gtk.Revealer):

    def __init__(self, label="", size=14):
        super().__init__()
        self.__content = Box(spacing=10)
        self.spin = Adw.Spinner.new()
        self.spin.props.width_request = 14
        self.spin.props.height_request = 14

        self.text = Gtk.Label.new(label)

        self.__content.append_all([self.spin, self.text])
        self.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)
        self.set_transition_duration(200)

        self.set_child(self.__content)

    def set_label(self, label):
        self.text.set_label(label)


class QuickBluetoothDevice(Gtk.Button):
    # TODO: Implement connecting to device

    def __init__(self, device: AstalBluetooth.Device):
        super().__init__(css_classes=["toggle-button"])
        self.device = device
        self.logger = getLogger("QuickBluetoothDevice")
        self.content = Box(spacing=10)
        self.revealer = RevealSpin()

        icon = Gtk.Image(icon_name="dialog-question-symbolic" if (
            i := device.get_icon()) is None else i)
        name = Gtk.Label(label=get_name_or_address(device),
                         xalign=0,
                         hexpand=True)

        self.connected = Gtk.Image()

        self.content.append_all([icon, name])
        self.content.append(self.connected)
        self.content.append(self.revealer)
        self.set_child(self.content)

        self.__toggle()
        self.device.connect("notify::connected", self.__toggle)
        self.connect("clicked", self.toggle_connection)

    def __toggle(self, *_):
        if "active" in self.get_css_classes():
            self.connected.set_visible(False)
            self.remove_css_class("active")
        else:
            self.connected.set_from_icon_name("emblem-ok-symbolic")
            self.connected.set_visible(True)
            self.add_css_class("active")

    def toggle_connection(self, *_):
        if self.device.get_connecting() != 0:
            notify(
                "BluetoothDevice",
                f"A connection is already in process. Device {self.name.get_label()}"
            )
            return
        if self.device.get_connected() is False:
            self.revealer.set_label("Connecting...")
            self.revealer.set_reveal_child(True)
            self.device.connect_device(self.__on_connected)
        else:
            self.revealer.set_label("Disconnecting...")
            self.revealer.set_reveal_child(True)
            self.device.disconnect_device(self.__on_disconnected)

    def __on_disconnected(self, _, res):
        self.__hide_revealer()
        try:
            self.device.disconnect_device_finish(res)
            XtrBluetooth.get_default().emit("device-disconnected", self.device)
        except:
            self.logger.exception('Error')

    def __on_connected(self, _, res):
        self.__hide_revealer()
        try:
            self.device.connect_device_finish(res)
            XtrBluetooth.get_default().emit("device-connected", self.device)
        except:
            self.logger.exception("Error")

    def __hide_revealer(self):
        self.__toggle()
        self.revealer.set_reveal_child(False)


class QuickBluetoothMenu(QuickMenu):

    def __init__(self):
        super().__init__("Bluetooth", logger_name="QuickBluetoothMenu")
        self.config: Config = Config.get_default()
        self.scanning = False
        self.__last_connected = None
        self.items = {}

        self.blue = XtrBluetooth.get_default()
        self.adapter = None
        self.scan_btt = Gtk.Button(icon_name="edit-find-symbolic",
                                   css_classes=["circular"],
                                   tooltip_text="Scan for devices")
        self.spinner = RevealSpin("Scanning...")

        self.blue.connect("notify::adapter", self.__change_adapter)
        self.blue.connect("notify::is-powered", self.__change_powered)
        self.__change_adapter()
        self.__change_powered()

        self.__add_bulk()
        self.blue.connect("device-added", self.__on_add)
        self.blue.connect("device-removed", self.__on_remove)
        self.blue.connect("device-connected", self.__on_connected)
        self.blue.connect("device-disconnected", self.__on_disconnected)
        self.scan_btt.connect("clicked", self.__toggle_scan)

        self.titlebar_pack_end(self.spinner)
        self.titlebar_pack_end(self.scan_btt)

    @GObject.Property(nick="last-connected-device")
    def last_connected_device(self):
        return self.__last_connected

    def __add_bulk(self):
        for device in self.blue.get_devices():
            self.__on_add(None, device)

    def __on_add(self, _, device: AstalBluetooth.Device):
        if self.config.quicksettings.quick_blue_show_no_name.value is False and device.get_name(
        ) == "":
            return
        name = get_name_or_address(device)
        self.items[name] = QuickBluetoothDevice(device)
        self.append(self.items[name])

    def __on_connected(self, _, device: AstalBluetooth.Device):
        name = get_name_or_address(device)
        if name in self.items:
            print(name)
            if device.get_connected() is True:
                self.__last_connected = device
                self.notify("last-connected-device")
                return
            else:
                self.logger.warning("Repeated device (%s). Skipping...", name)
                return

    def __on_disconnected(self, _, device: AstalBluetooth.Device):
        self.__last_connected = None
        self.notify("last-connected-device")

    def __on_remove(self, _, device: AstalBluetooth.Device):
        name = get_name_or_address(device)
        if name not in self.items:
            return
        self.remove(self.items.pop(name))

    def __change_adapter(self, *_):
        if self.blue.get_adapter() is None:
            self.__show_no_adapter_placeholder()
            self.adapter = None
        else:
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

    def on_children_change(self, *_):
        if len(self.content.children) == 1:
            self.set_placeholder_attrs(
                "Bluetooth", "No bluetooth devices available. Start a scan",
                "bluetooth-symbolic", True)
        else:
            self.set_placeholder_visibility(False)

    def __show_no_adapter_placeholder(self):
        self.set_placeholder_attrs("Bluetooth", "No bluetooth adapter found",
                                   "bluetooth-disabled-symbolic", True)

    def __show_disabled_placeholder(self):
        self.set_placeholder_attrs("Bluetooth", "The bluetooth is disabled",
                                   "bluetooth-disabled-symbolic", True)

    def __change_powered(self, *_):
        if self.adapter is None:
            return
        powered = self.blue.get_is_powered()
        self.scan_btt.set_sensitive(powered)
        if powered is False:
            self.__show_disabled_placeholder()
        else:
            self.on_children_change()


class QuickBluetooth(QuickButton):

    def __init__(self):
        super().__init__(icon=BluetoothIndicator(size=24,
                                                 _hide_if_no_adapter=False),
                         header="Bluetooth",
                         default_subtitle="Disabled")
        self.blue = AstalBluetooth.get_default()
        self.adapter = self.blue.get_adapter()
        self.__menu = QuickBluetoothMenu()

        self.blue.connect("notify::adapter", self.__on_adapter_change)
        self.blue.connect("notify::is-connected", self.__change_subtitle)
        self.blue.connect("notify::is-powered", self.__change_subtitle)
        self.__menu.bind_property("last-connected-device",
                                  self.heading,
                                  "label",
                                  GObject.BindingFlags.SYNC_CREATE,
                                  transform_to=self.__change_title)
        self.__change_subtitle()
        self.set_menu(self.__menu, "bluetooth")

    def __on_adapter_change(self, *_):
        self.adapter = self.blue.get_adapter()
        self.set_sensitive(not self.adapter is None)

    def set_active(self, active):
        if self.adapter is None:
            notify("QuickBluetooth", "No bluetooth adapters available")
            return
        self.active = active
        if active is True:
            self.button.add_css_class("active")
        else:
            self.button.remove_css_class("active")
        self.adapter.set_powered(self.active)

    def __change_title(self, *_):
        dev = self.__menu.last_connected_device
        if dev is None:
            self.heading.set_label("Bluetooth")
        else:
            self.heading.set_label(get_name_or_address(dev))

    def __change_subtitle(self, *_):
        if self.blue.get_is_connected():
            self.set_active(True)
            self.subtitle.set_label("Connected")
        elif self.blue.get_is_powered() is True:
            self.subtitle.set_text("Enabled")
            self.set_active(True)
        elif self.blue.get_is_powered() is False:
            self.subtitle.set_text("Disabled")
