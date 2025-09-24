from .modules.versions import init_libraries

init_libraries()

from .modules.logger import init_logger
from gi.repository import Adw, GLib, Gio, Gdk, Gtk

from .modules.style import compile_scss
from .widgets.bar import Bar
from .widgets.notifications import Notifications


class App(Adw.Application):
    instance = None

    def __init__(self):
        super().__init__(
            application_id="com.github.XtremeTHN.Shell",
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
        )

    def add_window(self, window, *args, **kwargs):
        super().add_window(window(*args, **kwargs))

    def apply_css(self):
        css = compile_scss()

        display = Gdk.Display.get_default()
        if not display:
            print("couldn't get display")
            return

        provider = Gtk.CssProvider.new()
        provider.load_from_string(css)

        Gtk.StyleContext.add_provider_for_display(
            display, provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

    # def open_inspector(self):
    #     # proxy = Gio.DBusProxy.new_for_bus_sync(
    #     #     Gio.BusType.SESSION,
    #     #     Gio.DBusProxyFlags.NONE,
    #     #     None,
    #     #     "com.github.XtremeTHN.Shell",
    #     #     "/com/github/XtremeTHN/Shell",
    #     #     "com.github.XtremeTHN.Shell",
    #     #     None
    #     # )

    #     # print("asd")
    #     # proxy.inspector()
    #     Gtk.

    def do_command_line(self, command_line):
        argv = command_line.get_arguments()

        if command_line.get_is_remote():
            # app already running
            self.open_inspector()

        else:
            init_logger()
            self.apply_css()
            self.add_window(Bar)
            self.add_window(Notifications)

        return 0


def run():
    GLib.set_prgname("shell")
    App.instance = App()

    try:
        App.instance.run()
    except KeyboardInterrupt:
        pass
