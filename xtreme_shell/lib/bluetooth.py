from gi.repository import AstalBluetooth

from .utils import GObject, Object


class XtrBluetooth(Object):
    __gsignals__ = {
        "device-connected": (
            GObject.SignalFlags.RUN_LAST,
            None,
            (AstalBluetooth.Device,),
        ),
        "device-disconnected": (
            GObject.SignalFlags.RUN_LAST,
            None,
            (AstalBluetooth.Device,),
        ),
        "device-added": (GObject.SignalFlags.RUN_LAST, None, (AstalBluetooth.Device,)),
        "device-removed": (
            GObject.SignalFlags.RUN_LAST,
            None,
            (AstalBluetooth.Device,),
        ),
    }
    devices = GObject.Property()
    adapter = GObject.Property(type=AstalBluetooth.Adapter, default=None)
    is_powered = GObject.Property(type=bool, default=False)

    def __init__(self):
        super().__init__()
        self.blue = AstalBluetooth.get_default()
        self.blue.connect("device-added", lambda *_: self.emit("device-added", *_[1:]))
        self.blue.connect(
            "device-removed", lambda *_: self.emit("device-removed", *_[1:])
        )
        self.blue.bind_property(
            "adapter", self, "adapter", GObject.BindingFlags.SYNC_CREATE
        )
        self.blue.bind_property(
            "is-powered", self, "is-powered", GObject.BindingFlags.SYNC_CREATE
        )

    def get_devices(self):
        return self.blue.get_devices()

    def get_is_powered(self):
        return self.is_powered

    def get_adapter(self):
        return self.adapter
