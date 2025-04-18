from gi.repository import AstalApps, Astal, Gtk, Gdk
from lib.utils import get_signal_args
from lib.variable import Variable
from lib.config import Config

from widgets.custom.box import Box
from subprocess import Popen, DEVNULL

import shlex

launched = Variable([])


class App(Gtk.Button):

    def __init__(self, app):
        super().__init__()
        __icon_name = app.get_icon_name()
        if __icon_name is None:
            __icon_name = "applications-other-symbolic"

        self.icon = Gtk.Image()
        if __icon_name.startswith("/") is True:
            self.icon.set_from_file(__icon_name)
        else:
            self.icon.set_from_icon_name(__icon_name)

        self.__app = app
        self.__content = Box(spacing=10)
        self.label = Gtk.Label.new(app.get_name())
        self.__content.append_all([self.icon, self.label])
        self.set_child(self.__content)

        self.connect("clicked", self.__on_clicked)

    def launch(self):
        self.__on_clicked(None)

    def __on_clicked(self, _):
        # exe = [x for x in shlex.split(self.__app.get_executable()) if x.startswith("%") is False or x.startswith("@") is False]
        # print(exe)
        
        # should_run.set_value(exe)
        self.__app.launch()
        launched.set_value(True)

class Content(Box):

    __gsignals__ = {"should-close": get_signal_args("run-first")}

    def __init__(self):
        super().__init__(vertical=True, spacing=10, css_classes=["box-10"])
        contr = Gtk.EventControllerKey.new()
        self.__apps = AstalApps.Apps.new()
        self.prefix = []

        self.entry = Gtk.Entry(placeholder_text="Search...")
        self.entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY,
                                           "edit-find-symbolic")
        self.scrollable = Gtk.ScrolledWindow(vexpand=True,
                                             css_classes=["card"])
        self.apps_widgets = Box(vertical=True,
                                spacing=5,
                                css_classes=["box-10"])

        self.scrollable.set_child(self.apps_widgets)
        self.append_all([self.entry, self.scrollable])

        self.__refresh()
        self.entry.connect("changed", self.__search)
        contr.connect("key-released", self.__on_key_released)
        launched.connect_notify(self.__on_launch)
        self.add_controller(contr)

    def __on_launch(self):
        self.emit("should-close")

    def reset(self):
        self.entry.set_text("")
        self.__refresh()

    def __on_key_released(self, _, val, code, state):
        if val == Gdk.KEY_Tab:
            return
        elif val == Gdk.KEY_Return:
            self.apps_widgets.children[0].launch()
        elif val == Gdk.KEY_Escape:
            # if entry is not focused grab focus
            if self.entry.get_state_flags() == 128:
                self.entry.grab_focus()
            # else close the window
            else:
                self.emit("should-close")

    def __search(self, _):
        apps = self.__apps.fuzzy_query(self.entry.get_text())
        self.__refresh(apps)

    def __refresh(self, apps=None):
        if apps is None:
            apps = self.__apps.get_list()
        self.apps_widgets.clear()
        self.apps_widgets.append_all([App(x) for x in apps])


class AppRunnerWindow(Astal.Window):

    def __init__(self):
        _conf = Config.get_default()
        super().__init__(namespace="astal-apprunner",
                         name="apprunner",
                         keymode=Astal.Keymode.ON_DEMAND,
                         layer=Astal.Layer.OVERLAY,
                         visible=_conf.apprunner.show_on_start.value,
                         width_request=400,
                         height_request=400,
                         resizable=False)

        self.__content = Content()
        self.__content.connect("should-close",
                               lambda _: self.set_visible(False))
        self.connect("notify::visible", self.__on_close)

        self.add_css_class("bordered")
        self.set_child(self.__content)
        self.present()

        self.set_visible(_conf.apprunner.show_on_start.value)

    @staticmethod
    def is_enabled():
        return Config.get_default().apprunner.enabled.value

    @staticmethod
    def parse_cmd_string(string: str):
        return shlex.split(string)

    def set_launch_prefix(self, prefix: list):
        self.__content.prefix = prefix

    def __on_close(self, *_):
        self.__content.reset()
