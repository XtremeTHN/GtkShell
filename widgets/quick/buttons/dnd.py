from widgets.custom.buttons import QuickUtilButton

from gi.repository import Gtk, AstalNotifd


class QuickDndButton(QuickUtilButton):
    def __init__(self):
        icon = Gtk.Image(icon_name="bell-outline-symbolic")
        super().__init__(
            icon=icon,
            header="Do not disturb",
            default_subtitle="Off",
            watch_property="dont-disturb",
            object=AstalNotifd.get_default(),
            cb=self.__on_changed,
        )
    
    def __on_changed(self, *_):
        if self.object.props.dont_disturb:
            self.subtitle.set_label("On")
            self.button.add_css_class("active")
        else:
            self.subtitle.set_label("Off")
            self.button.remove_css_class("active")
