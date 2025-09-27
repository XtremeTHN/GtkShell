from gi.repository import AstalNotifd, GObject, Gtk
from .item import Notification
import logging


class NotifDaemon:
    instance = None

    @classmethod
    def get_default(cls):
        if cls.instance is None:
            cls.instance = AstalNotifd.get_default()
        return cls.instance


class NotificationList(Gtk.ListBox):
    __gtype_name__ = "NotificationList"

    def __init__(self, dismissWhenClosed=True):
        super().__init__(
            selection_mode=Gtk.SelectionMode.NONE,
            css_classes=["boxed-list-separate", "notif-list"],
        )

        self.logger = logging.getLogger("NotificationList")
        self.__empty = True
        self.dismiss_when_closed = dismissWhenClosed

        self.notifs: dict[str, Notification] = {}

        self.notifd = NotifDaemon.get_default()
        self.notifd.connect("notified", self.on_notified)
        self.notifd.connect("resolved", self.on_resolved)

    @GObject.Property(type=bool, default=True)
    def empty(self):
        return self.__empty

    @empty.setter
    def empty(self, value):
        self.__empty = value
        self.notify("empty")

    def populate(self):
        for x in self.notifd.get_notifications():
            self.append_notification(x, False)

    def on_notified(self, _, id: int, replaced: bool):
        notif = self.notifd.get_notification(id)
        self.append_notification(notif, replaced)

    def on_resolved(self, _, id: int, reason: AstalNotifd.ClosedReason):
        if id not in self.notifs:
            self.logger.warning(f"Notification with id {id} not found")
            return

        notif = self.notifs.pop(id)
        self.remove(notif)

        # fixes a bug where the notif window freezes when empty
        if len(self.notifs) == 0:
            self.empty = True

    def append_notification(self, notif, replaced):
        w = Notification(notif, lambda id, reason: self.on_resolved(None, id, None))
        self.append(w)
        self.notifs[notif.get_id()] = w

        self.empty = False
