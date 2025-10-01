from .modules.versions import init_libraries

init_libraries()

from .modules.logger import init_logger
from gi.repository import Adw, GLib, Gio, Gdk, Gtk, AstalCava

from .widgets.bar import Bar
from .widgets.notifications import Notifications
from .widgets.control import ControlCenter
from .widgets.applications import AppRunner

import logging
import argparse


class App(Adw.Application):
    instance = None

    def __init__(self):
        super().__init__(
            application_id="com.github.XtremeTHN.XtremeShell",
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
        )

        self.logger = logging.getLogger("App")
        self.windows: list[Adw.Window] = []

    @property
    def display(self) -> Gdk.Display | None:
        if (d := Gdk.Display.get_default()) is not None:
            return d
        else:
            self.logger.fatal("Gdk.Display is None")

    def add_window(self, window, *args, **kwargs):
        win = window(*args, **kwargs)
        super().add_window(win)

        self.windows.append(win)

    def parse_args(self, argv):
        parser = argparse.ArgumentParser(exit_on_error=False, add_help=False)
        parser.add_argument(
            "-h",
            "--help",
            action="store_true",
        )
        parser.add_argument(
            "-q",
            "--quit",
            action="store_true",
            help="Quit the running instance of the application",
        )

        parser.add_argument(
            "-t", "--toggle", action="store", help="Toggle the visibility of a window"
        )

        parser.add_argument(
            "--launch-prefix",
            action="store",
            help="Sets the prefix of the command to run in app launcher",
        )

        return parser.parse_args(argv), parser

    def get_window(self, name) -> Gtk.Window:
        for x in self.windows:
            if x.get_name() != name:
                continue
            return x

    def handle_args(self, command_line):
        try:
            argv, parser = self.parse_args(command_line.get_arguments())

            if argv.quit:
                self.quit()

            if argv.help:
                command_line.print_literal(parser.format_help())

            if argv.toggle:
                if not (w := self.get_window(argv.toggle)):
                    command_line.printerr_literal("Window not found")
                else:
                    w.set_visible(not w.get_visible())

            if argv.launch_prefix:
                self.get_window("app-runner").cmd_prefix = argv.launch_prefix

        except argparse.ArgumentError as e:
            print(e)
            command_line.printerr_literal(
                f"<{e.__class__.__name__}>: error on argument {e.args[0].option_strings}. Check -h"
            )

    def init_windows(self):
        self.add_window(Bar)
        self.add_window(AppRunner)
        self.add_window(Notifications)
        self.add_window(ControlCenter)

    def do_command_line(self, command_line):
        if command_line.get_is_remote():
            self.handle_args(command_line)
            del command_line  # releases the caller process
        else:
            init_logger()
            self.init_windows()

        return 0


def run(argv):
    GLib.set_prgname("shell")
    App.instance = App()

    try:
        App.instance.run(argv)
    except KeyboardInterrupt:
        pass
    finally:
        if c := AstalCava.get_default():
            c.set_active(False)
