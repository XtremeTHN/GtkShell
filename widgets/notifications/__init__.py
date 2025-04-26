from gi.repository import Adw, Astal, AstalNotifd, Gtk

from lib.config import Config
from lib.logger import getLogger
from widgets.custom.box import Box
from widgets.notifications.item import Notification


class NotificationManager:
    def __init__(self, spacing=10, enable_timeout=True):
        self.enable_timeout = enable_timeout
        self.logger = getLogger("NotificationManager")
        self.content = Box(vertical=True, spacing=spacing, vexpand=True)
        self.notifd = AstalNotifd.get_default()
        self.list = {}

        # Connect signals
        self.notifd.connect("notified", self._on_notification_added)
        self.notifd.connect("resolved", self.__on_notification_removed)

    def set_box(self, box):
        self.content = box
        for x in self.list.values():
            self.content.append(x)

    def _on_notification_added(self, _, notif_id, replaced):
        if replaced:
            self.__on_notification_removed(
                None, notif_id, AstalNotifd.ClosedReason.UNDEFINED
            )

        notif = self.notifd.get_notification(notif_id)
        if notif is None:
            self.logger.warning("Notification should not be None")
            return

        widget = Notification(notif, self.enable_timeout)
        widget.connect("dismiss", self.__on_notification_removed)

        self.list[notif.get_id()] = widget
        self.content.append(widget)

    def __on_notification_removed(self, _, notif_id, reason: AstalNotifd.ClosedReason):
        widget = self.list.pop(notif_id, None)
        notif = self.notifd.get_notification(notif_id)
        if notif is not None:
            if reason == AstalNotifd.ClosedReason.DISMISSED_BY_USER:
                try:
                    notif.dismiss()
                except:  # noqa: E722
                    pass

        if widget:
            self.content.remove(widget)


class NotificationsWindow(Astal.Window):
    def __init__(self):
        super().__init__(
            name="notifications",
            namespace="astal-notifications",
            margin_top=10,
            css_classes=["nobackground-window"],
            resizable=False,
            anchor=Astal.WindowAnchor.TOP | Astal.WindowAnchor.RIGHT,
            layer=Astal.Layer.OVERLAY,
        )

        self.manager = NotificationManager()
        self.set_child(self.manager.content)
        self.manager.content.connect("notify::children", self.__on_children_changed)

        self.present()

    def __on_children_changed(self, *_):
        # if there's no children in the window, it will freeze
        # idk why, so i will hide it.
        self.set_visible(bool(self.manager.content.children))

    @staticmethod
    def is_enabled():
        return Config.get_default().notifications.enabled.value
