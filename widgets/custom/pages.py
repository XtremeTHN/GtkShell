from widgets.custom.box import Box
from gi.repository import Gtk

class QuickPage(Box):
    stack: Gtk.Stack = None
    def __init__(self, title: str, max_height=250):
        super().__init__(spacing=10, vertical=True)
        self.max_height = max_height
        self.top = Box(spacing=10)

        self.back_btt = Gtk.Button(icon_name="go-previous-symbolic", css_classes=["circular"])
        self.__title = Gtk.Label(label=title, css_classes=["title-3"])

        self.top.append_all([self.back_btt, self.__title])
        self.append(self.top)

    def set_child(self, child):
        self.append(Gtk.ScrolledWindow(css_classes=["box-10", "card"], child=child, vexpand=True, max_content_height=self.max_height))
