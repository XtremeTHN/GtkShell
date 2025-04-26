from gi.repository import Gtk

from widgets.custom.box import Box


class Header(Box):
    def __init__(self, title, show_close_btt=True):
        super().__init__(vertical=True)
        self.control = Gtk.CenterBox.new()

        self.title_widget = Gtk.Label(
            label=title,
            xalign=0,
            css_classes=["dimmed"],
            hexpand=True,
        )
        self.control.set_start_widget(self.title_widget)

        if show_close_btt:
            self.close_btt = Gtk.Button(
                icon_name="window-close-symbolic",
                css_classes=["flat"],
            )
            self.control.set_end_widget(self.close_btt)

        self.append(self.control)
        self.append(Gtk.Separator())

    def set_title_widget(self, widget):
        self.control.set_start_widget(widget)
