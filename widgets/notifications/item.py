from lib.utils import lookup_icon, get_signal_args, Timeout
from gi.repository import Gtk, Adw, AstalNotifd
from widgets.custom.icons import FramedImage
from widgets.custom.box import Box

from lib.config import Config

class Header(Box):

    def __init__(self, notif):
        super().__init__(css_classes=["header"], vertical=True)

        self.title_widget = Gtk.Label(
            label=notif.get_app_name(),
            xalign=0,
            css_classes=["dimmed"],
            hexpand=True,
        )
        self.close_btt = Gtk.Button(
            icon_name="window-close-symbolic",
            css_classes=["flat"],
        )

        control = Box()
        control.append_all([self.title_widget, self.close_btt])
        self.append(control)
        self.append(Gtk.Separator())


class NotifAction(Gtk.Button):

    def __init__(self, action: AstalNotifd.Action):
        super().__init__(label=action.label)
        self.id = action.id


# inherits from Adw.Bin to fix ugly shadows
class Notification(Adw.Bin):
    __gsignals__ = {
        "dismiss":
        get_signal_args("run-last", args=(int, AstalNotifd.ClosedReason))
    }

    def __init__(self, notif: AstalNotifd.Notification):
        super().__init__(
            margin_end=10,
            css_classes=["notification-wrap"],
        )

        content = Box(vertical=True, spacing=10, css_classes=["notification"])

        # Header
        self.header = Header(notif)
        content.append(self.header)

        # Content layout
        h_cont = Box(spacing=15)
        self.image = FramedImage(42)

        # Labels
        self.title = Gtk.Label(
            label=notif.get_summary(),
            xalign=0,
            use_markup=True,
            css_classes=["title-2"],
        )
        self.body = Gtk.Label(
            label=notif.get_body(),
            valign=Gtk.Align.CENTER,
            xalign=0,
            hexpand=True,
            wrap=True,
            use_markup=True,
            max_width_chars=24,
        )

        labels_box = Box(vertical=True)
        labels_box.append_all([self.title, self.body])

        # Optional image
        img = notif.get_image()
        if img:
            if not lookup_icon(img):
                self.image.set_from_file(img)
            else:
                self.image.set_from_icon_name(img)
            h_cont.append(self.image)

        h_cont.append(labels_box)
        content.append(h_cont)

        # Optional actions
        actions = notif.get_actions()
        if actions:
            actions_box = Box(spacing=5, homogeneous=True)
            for action in actions:
                action_btn = NotifAction(action)
                action_btn.connect("clicked", self.__invoke, notif)
                actions_box.append(action_btn)
            content.append(actions_box)

        self.set_child(content)

        # Connect close button
        self.header.close_btt.connect("clicked", self.__close, notif)

        if notif.get_expire_timeout() == -1:
            Timeout(lambda: self.__close(None, notif, AstalNotifd.ClosedReason.EXPIRED), Config.get_default().notifications.default_expire_timeout.value)

    def __invoke(self, button: NotifAction, notif):
        notif.invoke(button.id)

    def __close(self, _, notif, reason=AstalNotifd.ClosedReason.DISMISSED_BY_USER):
        self.emit("dismiss", notif.get_id(),
                  reason)
