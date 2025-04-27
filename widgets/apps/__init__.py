from gi.repository import Astal, AstalApps, Gdk, GLib, GObject, Gtk

from lib.config import Config
from lib.utils import lookup_icon
from lib.variable import Variable
from widgets.custom.box import Box
from widgets.custom.widget import CustomizableWidget

should_close = Variable(False)
_conf = Config.get_default().applauncher


class AppItem(Gtk.Button):
    def __init__(self, app: AstalApps.Application):
        super().__init__(css_classes=["flat"], tooltip_text=app.get_name())
        self.app = app

        icon_name = app.get_icon_name()
        icon = Gtk.Image(pixel_size=46)
        if icon_name is None:
            icon_name = "item-missing-symbolic"
        if GLib.file_test(icon_name, GLib.FileTest.EXISTS):
            icon.set_from_file(icon_name)
        elif lookup_icon(icon_name):
            icon.set_from_icon_name(icon_name)
        else:
            icon.set_from_icon_name("item-missing-symbolic")

        self.set_child(icon)

        self.connect("clicked", self.__on_clicked)

    def __on_clicked(self, _):
        self.app.launch()
        should_close.set_value(True)


class Content(Box):
    def __init__(self):
        super().__init__(css_classes=["box-10"], vertical=True, spacing=10)
        contr = Gtk.EventControllerKey.new()
        self.apps = AstalApps.Apps.new()

        self.entry = Gtk.SearchEntry(placeholder_text="Search for an app")
        scrolled = Gtk.ScrolledWindow(max_content_height=350, vexpand=True)
        self.apps_widget = Gtk.FlowBox(max_children_per_line=6, vexpand=True)

        scrolled.set_child(self.apps_widget)
        self.append_all([self.entry, scrolled])
        self.add_controller(contr)

        # Connections
        self.apps_widget.connect("child-activated", self.__on_child_activated)
        self.entry.connect("search-changed", self.__refresh)
        contr.connect("key-released", self.__on_key_released)

        _conf.search_delay.on_change(self.__change_delay, once=True)
        self.__refresh()

    def reset(self):
        self.entry.set_text("")
        self.__refresh()

    def __change_delay(self, *_):
        self.entry.set_search_delay(_conf.search_delay.value)

    def __on_key_released(self, _, val, code, state):
        if val == Gdk.KEY_Tab:
            return
        elif val == Gdk.KEY_Escape:
            # if entry is not focused grab focus
            if self.entry.get_state_flags() == 128:
                self.entry.grab_focus()
            # else close the window
            else:
                should_close.set_value(True)

    def __on_child_activated(self, _, item: Gtk.FlowBoxChild):
        item: AppItem = item.get_child()
        item.app.launch()
        should_close.set_value(True)

    def __refresh(self, *_):
        text = self.entry.get_text()
        # clear the widget
        while (w := self.apps_widget.get_first_child()) is not None:
            self.apps_widget.remove(w)

        for x in self.apps.fuzzy_query(text):
            item = AppItem(x)
            self.apps_widget.append(item)


class ApplicationLauncher(Astal.Window, CustomizableWidget):
    def __init__(self):
        Astal.Window.__init__(
            self,
            name="applauncher",
            namespace="astal-apps",
            resizable=False,
            width_request=400,
            height_request=150,
            keymode=Astal.Keymode.ON_DEMAND,
            layer=Astal.Layer.OVERLAY,
        )

        CustomizableWidget.__init__(self)
        self._conf = Config.get_default().applauncher
        self.content = Content()
        self.add_css_class("bordered")
        self.set_child(self.content)
        self.present()

        self.background_opacity = self._conf.background_opacity
        self.background_opacity.on_change(self.change_opacity, once=True)

        should_close.connect_notify(self.__close)
        self.connect("notify::visible", self.__on_visible)

        self.set_visible(self._conf.show_on_start.value)

    def __on_visible(self, *_):
        if self.get_visible():
            self.content.entry.grab_focus()

    def __close(self):
        if should_close.get_value():
            self.set_visible(False)
            self.content.reset()
            should_close.set_value(False)

    @staticmethod
    def is_enabled():
        return Config.get_default().applauncher.enabled.value
