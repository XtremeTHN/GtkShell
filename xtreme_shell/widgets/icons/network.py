from gi.repository import AstalNetwork, Gtk, GObject
import logging


class NetworkIcon(Gtk.Image):
    __gtype_name__ = "NetworkIcon"

    def __init__(self, size=16):
        super().__init__(pixel_size=size)

        self.logger = logging.getLogger("NetworkIcon")
        self.net = AstalNetwork.get_default()

        self.net.connect("notify", self.change_obj)
        self.change_obj()

    def on_state_change(self, _, state: AstalNetwork.DeviceState):
        match state:
            case AstalNetwork.DeviceState.ACTIVATED:
                return "Connected (wired)"
            case AstalNetwork.DeviceState.DEACTIVATING:
                return "Disconnecting..."
            case AstalNetwork.DeviceState.DISCONNECTED:
                return "Disconnected"
            case _:
                return AstalNetwork.DeviceState.value.name.title()

    def change_obj(self, *_):
        device = None
        if (v := self.net.get_wifi()) is not None:
            device = v
            device.bind_property(
                "ssid", self, "tooltip-text", GObject.BindingFlags.SYNC_CREATE
            )
            self.logger.info("Wifi device detected")

        if (v := self.net.get_wired()) is not None:
            device = v

            device.bind_property(
                "state",
                self,
                "tooltip-text",
                GObject.BindingFlags.SYNC_CREATE,
                transform_to=self.on_state_change,
            )

            self.logger.info("Wired device detected")
            if device:
                self.logger.info("Replaced wifi with ethernet")

        if device is not None:
            device.bind_property(
                "icon-name", self, "icon-name", GObject.BindingFlags.SYNC_CREATE
            )
            self.logger.info("Icon binded")
