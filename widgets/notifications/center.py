from gi.repository import Astal, Gtk

from lib.config import Config
from widgets.custom.box import Box, QuickMenu
from widgets.custom.header import Header
from widgets.notifications import NotificationManager


class Content(Box):
    def __init__(self):
        super().__init__(
            css_classes=["box-10", "bordered", "background-box"],
            margin_start=10,
            vertical=True,
            spacing=10,
        )
        label = Gtk.Label(label="Notifications", css_classes=["title-2"])
        header = Header("Notifications", show_close_btt=False)
        header.set_title_widget(label)

        menu = QuickMenu("", show_top_bar=False, logger_name="NotificationCenter")
        menu.set_placeholder_attrs(
            "Notification Center", "No notifications yet", "bell-outline"
        )
        menu.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        manager = NotificationManager(spacing=0, enable_timeout=False)
        manager.set_box(menu)
        for x in manager.notifd.get_notifications():
            manager._on_notification_added(None, x.get_id(), False)

        self.append_all([header, menu])


class NotificationCenter(Astal.Window):
    def __init__(self):
        super().__init__(
            namespace="astal-notif-center",
            css_classes=[],
            name="notification-center",
            anchor=Astal.WindowAnchor.LEFT,
            layer=Astal.Layer.OVERLAY,
            resizable=False,
            width_request=350,
            height_request=600,
        )

        self.content = Content()

        self.set_child(self.content)
        self.present()

    @staticmethod
    def is_enabled() -> bool:
        return Config.get_default().notifications.center.enabled.value
