from gi.repository import Adw, Astal, AstalNotifd, Gtk

from lib.config import Config
from lib.logger import getLogger
from widgets.custom.box import Box
from widgets.notifications.item import Notification


class NotificationList(Box):
    def __init__(self):
        super().__init__(vertical=True, spacing=10)
        self.logger = getLogger("Notifications")
        self.notifd = AstalNotifd.get_default()
        self.list = {}

        # Connect signals
        self.notifd.connect("notified", self.__on_notification_added)
        self.notifd.connect("resolved", self.__on_notification_removed)
        self.connect("notify::children", self.__on_children_changed)

    def __on_children_changed(self, *_):
        # if there's no children in the window, it will freeze
        # idk why, so i will hide it.
        self.set_visible(bool(self.children))

    def __on_notification_added(self, _, notif_id, replaced):
        if replaced:
            self.__on_notification_removed(
                None, notif_id, AstalNotifd.ClosedReason.UNDEFINED
            )

        notif = self.notifd.get_notification(notif_id)
        if notif is None:
            self.logger.warning("Notification should not be None")
            return

        widget = Notification(notif)
        widget.connect("dismiss", self.__on_notification_removed)

        self.list[notif.get_id()] = widget
        self.append(widget)

    def __on_notification_removed(self, _, notif_id, reason: AstalNotifd.ClosedReason):
        widget = self.list.pop(notif_id, None)
        notif = self.notifd.get_notification(notif_id)

        if widget:
            if reason == AstalNotifd.ClosedReason.DISMISSED_BY_USER:
                notif.dismiss()
            self.remove(widget)
        else:
            if notif is None:
                self.logger.warning(
                    "Recieved resolve signal but no notification with id of %d",
                    notif_id,
                )
                return
            notif.dismiss()


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

        self.content = NotificationList()
        self.set_child(self.content)

        self.present()

    @staticmethod
    def is_enabled():
        return Config.get_default().notifications.enabled.value
