from gi.repository import AstalNetwork, GObject, GLib, Gtk

from ..icons.network import Network
from .button import QuickButton, ButtonService


class NetManager(ButtonService):
    def __init__(self, button: QuickButton):
        super().__init__(button)

        self.net = Network.get_default()

        self.net.bind_property(
            "icon-name",
            button,
            "btt-icon-name",
            GObject.BindingFlags.SYNC_CREATE,
        )

        self.net.connect("notify::tooltip-text", self.on_tooltip_change)

        self.net.bind_property(
            "active",
            self,
            "active",
            GObject.BindingFlags.SYNC_CREATE,
        )

        self.bind_lock("wired", self.net.net)

        button.connect("clicked", self.on_clicked)
        self.on_tooltip_change()

    def on_tooltip_change(self, *_):
        self.widget.subtitle.set_visible(len(self.net.tooltip_text) != 0)
        self.widget.subtitle.set_label(self.net.tooltip_text)
