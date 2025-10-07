from gi.repository import AstalBluetooth, GObject, Gtk
from .button import QuickButton
import logging


class BluetoothManager(GObject.GObject):
    def __init__(self, button: QuickButton):
        super().__init__()
        self.logger = logging.getLogger("BluetoothManager")
        self.widget = button
        self.__active = False
        self.blue = AstalBluetooth.get_default()

        self.blue.connect("notify::is-connected", self.change_connected)
        self.blue.connect("notify::adapter", self.on_adapter_change)

        self.on_adapter_change()
        button.connect("clicked", self.on_clicked)

    def change_connected(self, *_):
        for x in self.blue.get_devices():
            if x.props.connected is False:
                continue

            self.widget.subtitle.set_label(
                n if (n := x.get_name()) not in [None, ""] else x.get_address()
            )

            self.widget.subtitle.set_visible(True)

    def on_clicked(self, _):
        self.active = not self.active

    @GObject.Property(type=bool, default=False)
    def active(self):
        return self.__active

    @active.setter
    def active(self, value):
        self.__active = value if self.adapter is not None else False
        self.notify("active")
        self.adapter.set_powered(value)

        if self.widget.subtitle.get_visible():
            self.widget.subtitle.set_visible(value)
            self.widget.subtitle.set_label("")

        self.widget.add_css_class(
            "active"
        ) if self.__active else self.widget.remove_css_class("active")

        self.widget.icon.set_from_icon_name(
            "bluetooth-symbolic" if self.__active else "bluetooth-disabled-symbolic"
        )

    @GObject.Property()
    def adapter(self) -> AstalBluetooth.Adapter:
        adapters = self.blue.get_adapters()
        return adapters[0] if len(adapters) > 0 else None

    def on_adapter_change(self, *_):
        adapter = self.blue.get_adapter()
        self.logger.info(f"New adapter: {adapter.get_name()}")

        if not adapter:
            self.widget.icon.set_from_icon_name("bluetooth-disabled-symbolic")
            return

        self.active = adapter.get_powered()
