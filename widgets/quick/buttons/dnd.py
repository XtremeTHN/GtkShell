from gi.repository import AstalNotifd, Gtk

from widgets.custom.buttons import QuickUtilButton


class QuickDndButton(QuickUtilButton):
    def __init__(self):
        icon = Gtk.Image(icon_name="bell-outline-symbolic")
        super().__init__(
            icon=icon,
            header="Dnd",
            default_subtitle="Off",
            watch_property="dont-disturb",
            object=AstalNotifd.get_default(),
            has_menu=False,
            cb=self.__on_changed,
        )

        self.connect("activated", self.on_activate)
        self.connect("deactivated", self.on_deactivate)

    def on_activate(self, _):
        self.object.set_dont_disturb(True)

    def on_deactivate(self, _):
        self.object.set_dont_disturb(False)

    def __on_changed(self, *_):
        if self.object.props.dont_disturb:
            self.subtitle.set_label("On")
            self.button.add_css_class("active")
        else:
            self.subtitle.set_label("Off")
            self.button.remove_css_class("active")
