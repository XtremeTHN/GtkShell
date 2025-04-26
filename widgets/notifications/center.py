from gi.repository import Adw, Astal, Gtk

from lib.config import Config
from widgets.custom.box import Box, QuickMenu
from widgets.custom.header import Header
from widgets.custom.widget import CustomizableWidget
from widgets.notifications import NotificationManager


class Content(Box, CustomizableWidget):
    def __init__(self):
        Box.__init__(
            self,
            css_classes=["box-10", "bordered", "background-box"],
            margin_start=10,
            vertical=True,
            spacing=10,
        )
        CustomizableWidget.__init__(self)

        self.background_opacity = (
            Config.get_default().notifications.center.background_opacity
        )
        label = Gtk.Label(label="Notifications", css_classes=["title-2"])
        header = Header("Notifications", show_close_btt=False)
        header.set_title_widget(label)

        menu = QuickMenu("", show_top_bar=False, logger_name="NotificationCenter")
        menu.set_placeholder_attrs(
            "Notification Center", "No notifications yet", "bell-outline"
        )
        menu.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.manager = NotificationManager(spacing=0, enable_timeout=False)
        self.manager.set_box(menu)
        for x in self.manager.notifd.get_notifications():
            self.manager._on_notification_added(None, x.get_id(), False)

        cnt = Adw.ButtonContent(icon_name="edit-clear-all", label="Clear All")
        rm_btt = Gtk.Button(child=cnt)
        rm_btt.connect("clicked", self.__on_clear_clicked)

        self.append_all([header, menu, rm_btt])

        self.background_opacity.on_change(self.change_opacity, once=True)

    def __on_clear_clicked(self, _):
        for x in self.manager.notifd.get_notifications():
            x.dismiss()


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

        self.set_visible(Config.get_default().notifications.center.show_on_start.value)

    @staticmethod
    def is_enabled() -> bool:
        return Config.get_default().notifications.center.enabled.value
