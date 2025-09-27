from gi.repository import Astal, Gtk, GObject
import logging

from .list import NotificationList


class Notifications(Astal.Window):
    notif_list: Gtk.ListBox

    def __init__(self):
        super().__init__(
            name="notifications",
            namespace="shell-notifications",
            anchor=Astal.WindowAnchor.TOP | Astal.WindowAnchor.RIGHT,
            layer=Astal.Layer.OVERLAY,
            margin_end=10,
            css_classes=[],
        )

        self.logger = logging.getLogger("Notifications")

        self.setup_widgets()
        self.present()

    def setup_widgets(self):
        self.notif_list = NotificationList(dismissWhenClosed=False)
        self.notif_list.bind_property(
            "empty", self, "visible", GObject.BindingFlags.INVERT_BOOLEAN
        )
        self.set_child(self.notif_list)
