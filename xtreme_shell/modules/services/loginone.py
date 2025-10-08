from gi.repository import GObject, Gio, GLib


class LoginOne(GObject.Object):
    instance = None

    def __init__(self):
        super().__init__()

        self.proxy = Gio.DBusProxy.new_for_bus_sync(
            Gio.BusType.SYSTEM,
            Gio.DBusProxyFlags.NONE,
            None,
            "org.freedesktop.login1",
            "/org/freedesktop/login1",
            "org.freedesktop.login1.Manager",
        )

        self.session_proxy = Gio.DBusProxy.new_for_bus_sync(
            Gio.BusType.SYSTEM,
            Gio.DBusProxyFlags.NONE,
            None,
            "org.freedesktop.login1",
            "/org/freedesktop/login1/session/auto",
            "org.freedesktop.login1.Session",
        )

    def can_suspend(self) -> bool:
        return self.call("CanSuspend", None).unpack()[0] == "yes"

    def interactive(self, value):
        return GLib.Variant("(b)", (value,))

    def call(self, method, args: GLib.Variant | None, proxy=None):
        proxy = proxy or self.proxy
        return proxy.call_sync(method, args, Gio.DBusCallFlags.NONE, -1, None)

    def suspend(self):
        if self.can_suspend() is False:
            return False

        self.call("Suspend", self.interactive(False))

    def power_off(self):
        self.call("PowerOff", self.interactive(False))

    def log_out(self):
        return self.call("Terminate", None, proxy=self.session_proxy)

    def lock(self):
        return self.call("Lock", None, proxy=self.session_proxy)

    @classmethod
    def get_default(cls):
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance
