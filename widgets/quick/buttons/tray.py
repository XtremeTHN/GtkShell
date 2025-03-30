from widgets.custom.buttons import QuickButton
from gi.repository import Gtk, AstalTray

class QuickSysTray(QuickButton):
    def __init__(self):
        self.icon = Gtk.Image(icon_name="system-run-symbolic", pixel_size=24)
        super().__init__(icon=self.icon, header="System tray", default_subtitle="No applications")

        self.tray = AstalTray.get_default()

        self.tray.connect("notify::items", self.__on_tray_change)

    def __on_tray_change(self, *_):
        if len(self.tray.props.items) == 0:
            self.subtitle.set_text("No applications")
            self.set_active(False)
            return
        else:
            self.subtitle.set_text(f"{len(self.tray.props.items)} applications")
            self.set_active(True)