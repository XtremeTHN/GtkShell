from gi.repository import AstalNotifd, Astal, Adw, Gtk
from widgets.notifications.item import Notification
from widgets.custom.box import Box
from lib.logger import getLogger
from lib.config import Config


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

        self.logger = getLogger("Notifications")
        self.notifd = AstalNotifd.get_default()
        self.list = {}

        self.content = Box(vertical=True, spacing=10)
        self.set_child(self.content)

        # Connect signals
        self.notifd.connect("notified", self.__on_notification_added)
        self.notifd.connect("resolved", self.__on_notification_removed)
        self.content.connect("notify::children", self.__on_children_changed)

        self.present()

    def __on_children_changed(self, *_):
        # if there's no children in the window, it will freeze
        # idk why, so i will hide it.
        self.set_visible(bool(self.content.children))

    def __on_notification_added(self, _, notif_id, replaced):
        if replaced:
            self.__on_notification_removed(None, notif_id,
                                          AstalNotifd.ClosedReason.UNDEFINED)

        notif = self.notifd.get_notification(notif_id)
        if notif is None:
            self.logger.warning("Notification should not be None")
            return

        widget = Notification(notif)
        widget.connect("dismiss", self.__on_notification_removed)

        self.list[notif.get_id()] = widget
        self.content.append(widget)

    def __on_notification_removed(self, _, notif_id,
                                  reason: AstalNotifd.ClosedReason):
        widget = self.list.pop(notif_id, None)
        notif = self.notifd.get_notification(notif_id)

        if widget:
            if reason == AstalNotifd.ClosedReason.DISMISSED_BY_USER:
                notif.dismiss()
            self.content.remove(widget)
        else:
            if notif is None:
                self.logger.warning("Recieved resolve signal but no notification with id of %d", notif_id)
                return
            notif.dismiss()

    @staticmethod
    def is_enabled():
        return Config.get_default().notifications.enabled.value
