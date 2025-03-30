from gi.repository import Gtk
from lib.utils import Box

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

class StatusPage(Box):
    def __init__(self, title=None, description=None, icon=None):
        super().__init__(vertical=True, vexpand=True, valign=Gtk.Align.CENTER)
        self.__title = Gtk.Label(label=title, css_classes=["title-3"])
        self.__description = Gtk.Label(label=description, css_classes=["dimmed"])
        self.__icon = Gtk.Image(icon_name=icon, pixel_size=28, margin_bottom=10)

        self.append_all([self.__icon, self.__title, self.__description])
    
    def set_title(self, title):
        self.__title.set_label(title)
    
    def set_description(self, desc):
        self.__description.set_label(desc)
    
    def set_icon_name(self, icon_name):
        self.__icon.set_from_icon_name(icon_name)