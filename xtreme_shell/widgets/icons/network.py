from gi.repository import AstalNetwork, Gtk, GObject
import logging


class Network(GObject.Object):
    instance = None

    tooltip_text = GObject.Property(type=str)
    icon_name = GObject.Property(type=str)

    active = GObject.Property(type=bool, default=False)

    def __init__(self):
        super().__init__()

        self.logger = logging.getLogger("Network")

        self.net = AstalNetwork.get_default()
        self.net.connect("notify", self.change_obj)

        self.change_obj()

    def on_state_change(self, _, state: AstalNetwork.DeviceState):
        state_str = ""
        match state:
            case AstalNetwork.DeviceState.ACTIVATED:
                self.active = True
                state_str = "Connected (wired)"
            case AstalNetwork.DeviceState.DEACTIVATING:
                self.active = False
                state_str = "Disconnecting..."
            case AstalNetwork.DeviceState.DISCONNECTED:
                self.active = False
                state_str = "Disconnected"
            case _:
                self.active = False
                state_str = AstalNetwork.DeviceState.value.name.title()

        self.notify("active")
        return state_str

    def change_obj(self, *_):
        device = None
        if (v := self.net.get_wifi()) is not None:
            device = v
            device.bind_property(
                "ssid", self, "tooltip-text", GObject.BindingFlags.SYNC_CREATE
            )
            self.logger.info("Wifi device detected")

        if (v := self.net.get_wired()) is not None:
            v.bind_property(
                "state",
                self,
                "tooltip-text",
                GObject.BindingFlags.SYNC_CREATE,
                transform_to=self.on_state_change,
            )

            self.logger.info("Wired device detected")
            if device:
                self.logger.info("Replaced wifi with ethernet")
            device = v

        if device is not None:
            device.bind_property(
                "icon-name", self, "icon-name", GObject.BindingFlags.SYNC_CREATE
            )
            self.logger.info("Icon binded")

    @classmethod
    def get_default(cls):
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance


class NetworkIcon(Gtk.Image):
    __gtype_name__ = "NetworkIcon"

    def __init__(self, size=16):
        super().__init__(pixel_size=size)

        net = Network.get_default()

        net.bind_property(
            "tooltip-text", self, "tooltip-text", GObject.BindingFlags.SYNC_CREATE
        )

        net.bind_property(
            "icon-name", self, "icon-name", GObject.BindingFlags.SYNC_CREATE
        )
