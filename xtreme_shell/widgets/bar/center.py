from gi.repository import Gtk, Astal
from ..notifications.item import Notification
from ..notifications.list import NotifDaemon

from xtreme_shell.modules.utils import Blp
import logging


@Blp("center")
class Center(Astal.Window):
    __gtype_name__ = "Center"
    stack: Gtk.Stack = Gtk.Template.Child()
    notif_list: Gtk.ListBox = Gtk.Template.Child()

    clear_btt: Gtk.Button = Gtk.Template.Child()

    def __init__(self):
        super().__init__(
            name="center",
            namespace="shell-center",
            anchor=Astal.WindowAnchor.TOP,
            margin_start=10,
            width_request=500,
            height_request=400,
        )

        self.logger = logging.getLogger("Center")

        self.notifs = {}
        self.notifd = NotifDaemon.get_default()

        self.notifd.connect("notified", self.on_notified)
        self.notifd.connect("resolved", self.on_resolved)

        notifs = self.notifd.get_notifications()

        self.clear_btt.set_sensitive(len(notifs) > 0)
        for x in notifs:
            self.on_notified(None, x.get_id(), False)

    @Gtk.Template.Callback()
    def clear_notifs(self, _):
        for x in self.notifd.get_notifications():
            x.dismiss()

    def on_resolved(self, _, id, reason):
        if id not in self.notifs:
            self.logger.warning(f"Notification with id {id} not found")
            return

        notif = self.notifs[id]

        if reason == "dismissed":
            notif.notif.dismiss()
        elif reason != "expired":
            del self.notifs[id]
            self.notif_list.remove(notif)

        if len(self.notifs) == 0:
            self.stack.set_visible_child_name("placeholder")
            self.clear_btt.set_sensitive(False)

    def on_notified(self, _, id, replaced):
        w = Notification(
            self.notifd.get_notification(id),
            lambda id, reason: self.on_resolved(None, id, reason),
        )
        self.notifs[id] = w
        self.notif_list.append(w)

        if self.stack.get_visible_child_name() == "placeholder":
            self.stack.set_visible_child_name("list")
            self.clear_btt.set_sensitive(True)
