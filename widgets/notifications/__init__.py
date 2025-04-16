from gi.repository import AstalNotifd, Astal, Adw, Gtk
from widgets.notifications.item import Notification
from widgets.custom.box import Box
from lib.logger import getLogger

from lib.config import Config


class NotificationsWindow(Astal.Window):

    def __init__(self):
        super().__init__(name="notifications",
                         namespace="astal-notifications",
                         margin_top=10,
                         css_classes=["nobackground-window"],
                         resizable=False,
                         anchor=Astal.WindowAnchor.TOP
                         | Astal.WindowAnchor.RIGHT,
                         layer=Astal.Layer.OVERLAY)
        self.logger = getLogger("Notifications")

        self.notifd = AstalNotifd.get_default()
        self.content = Box(vertical=True, spacing=10)
        self.list = {}

        self.notifd.connect("notified", self.__add_notification)
        self.notifd.connect("resolved", self.__remove_notification)
        self.content.connect("notify::children", self.__on_children_changed)
        map(lambda n: self.__add_notification(None, n),
            self.notifd.props.notifications)

        self.set_child(self.content)
        self.present()

    def __on_children_changed(self, *_):
        # when there's no child, the window will freeze, idk why
        # so i will hide it
        if len(self.content.children) == 0:
            self.set_visible(False)
        else:
            self.set_visible(True)

    def __add_notification(self, _, _id, replaced):
        # TODO: trigger the animation
        if replaced is True:
            self.__remove_notification(None, _id,
                                       AstalNotifd.ClosedReason.UNDEFINED)

        notif = self.notifd.get_notification(_id)
        w = Notification(notif)
        self.list[notif.get_id()] = w
        w.connect("dismiss", self.__remove_notification)
        self.content.append(w)

    def __remove_notification(self, _, _id, reason: AstalNotifd.ClosedReason):
        # TODO: trigger the close animation and wait for it and then closing the Notification
        if _id in self.list:
            w = self.list.pop(_id)
            self.content.remove(w)
            w.unmap()
        else:
            self.logger.warning(
                "Remove notification signal recieved, but there's no notification with id of %d",
                _id)

    @staticmethod
    def is_enabled():
        return Config.get_default().notifications.enabled.value
