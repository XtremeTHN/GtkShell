from .modules.versions import init_libraries

init_libraries()

from .modules.logger import init_logger
from gi.repository import Adw, GLib, Gio, Gdk, Gtk

from .modules.constants import SOURCE_DIR
from .modules.style import compile_scss
from .widgets.bar import Bar
from .widgets.notifications import Notifications
from .widgets.control import ControlCenter

import logging
import argparse


class App(Adw.Application):
    instance = None

    def __init__(self):
        super().__init__(
            application_id="com.github.XtremeTHN.Shell",
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
        )

        self.logger = logging.getLogger("App")

    @property
    def display(self) -> Gdk.Display | None:
        if (d := Gdk.Display.get_default()) is not None:
            return d
        else:
            self.logger.fatal("Gdk.Display is None")

    def add_window(self, window, *args, **kwargs):
        super().add_window(window(*args, **kwargs))

    def apply_css(self):
        css = compile_scss()

        provider = Gtk.CssProvider.new()
        provider.load_from_string(css)

        Gtk.StyleContext.add_provider_for_display(
            self.display, provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

    def parse_args(self, argv):
        parser = argparse.ArgumentParser(exit_on_error=False, add_help=False)
        parser.add_argument(
            "-q",
            "--quit",
            action="store_true",
            help="Quit the running instance of the application",
        )

        return parser.parse_args(argv)

    def do_command_line(self, command_line):
        argv = self.parse_args(command_line.get_arguments())

        if command_line.get_is_remote():
            if argv.quit:
                self.quit()
        else:
            init_logger()
            self.apply_css()
            self.add_window(Bar)
            self.add_window(Notifications)
            self.add_window(ControlCenter)

            Gtk.IconTheme.get_for_display(self.display).add_search_path(
                str(SOURCE_DIR / "icons")
            )

        return 0


def run(argv):
    GLib.set_prgname("shell")
    App.instance = App()

    try:
        App.instance.run(argv)
    except KeyboardInterrupt:
        pass
