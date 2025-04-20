from gi.repository import Astal, AstalApps, Gtk, GLib
from widgets.custom.box import Box
from lib.variable import Variable
from lib.utils import lookup_icon
from lib.config import Config

from widgets.custom.widget import CustomizableWidget


should_close = Variable(False)
class AppItem(Gtk.Button):
    def __init__(self, app: AstalApps.Application):
        super().__init__(css_classes=["flat"], tooltip_text=app.get_name())
        self.app = app

        icon_name = app.get_icon_name() or "item-missing-symbolic"
        icon = Gtk.Image(pixel_size=46)

        if GLib.file_test(icon_name, GLib.FileTest.EXISTS):
            icon.set_from_file(icon_name)
        elif lookup_icon(icon_name):
            icon.set_from_icon_name(icon_name)
        
        self.set_child(icon)

        self.connect("clicked", self.__on_clicked)
    
    def __on_clicked(self, _):
        self.app.launch()
        should_close.set_value(True)

class Content(Box):
    def __init__(self):
        Box.__init__(self, css_classes=["box-10", "shadow-box"], vertical=True, spacing=10)

        self.apps = AstalApps.Apps.new()
        
        self.entry = Gtk.SearchEntry()
        scrolled = Gtk.ScrolledWindow(max_content_height=350, vexpand=True)
        self.apps_widget = Gtk.FlowBox(max_children_per_line=6, vexpand=True)
        
        scrolled.set_child(self.apps_widget)
        self.append_all([self.entry, scrolled])

        # Connections
        self.apps_widget.connect("child-activated", self.__on_child_activated)
        self.entry.connect("search-changed", self.__refresh)
        self.__refresh()
    
    def reset(self):
        self.entry.set_text("")
        self.__refresh()
    
    def __on_child_activated(self, _, item: Gtk.FlowBoxChild):
        item: AppItem = item.get_child()
        item.app.launch()
        should_close.set_value(True)
    
    def __refresh(self, *_):
        text = self.entry.get_text()
        # clear the widget
        while (w:=self.apps_widget.get_first_child()) is not None:
            self.apps_widget.remove(w)
        
        for x in self.apps.fuzzy_query(text):
            item = AppItem(x)
            self.apps_widget.append(item)

class ApplicationLauncher(Astal.Window, CustomizableWidget):
    def __init__(self):
        Astal.Window.__init__(self, name="applauncher",
                         namespace="astal-apps",
                         resizable=False,
                         width_request=400,
                         height_request=150,
                         keymode=Astal.Keymode.ON_DEMAND,
                         layer=Astal.Layer.OVERLAY)
        
        CustomizableWidget.__init__(self)
        self._conf = Config.get_default().applauncher
        self.content = Content()
        self.add_css_class("bordered")
        self.set_child(self.content)
        self.present()
        
        self.background_opacity = self._conf.background_opacity
        self.background_opacity.on_change(self.change_opacity, once=True)

        should_close.connect_notify(self.__close)

        self.set_visible(self._conf.show_on_start.value)
    
    def __close(self):
        if should_close.get_value():
            self.hide()
            should_close.set_value(False)
    
    @staticmethod
    def is_enabled():
        return Config.get_default().applauncher.enabled.value