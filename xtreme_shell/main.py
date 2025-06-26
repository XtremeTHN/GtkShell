from .modules.style import compile_scss, get_colors_watcher
from .modules.logger import init_logger
from setproctitle import setproctitle
from .components.bar import Bar
from .widgets.corners import CornerWindow

import argparse
import logging

from gi.repository import Astal, Adw, GLib


class GtkShellApp(Astal.Application):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("GtkShellApp")

    def parse_args(self, args=None):
        parser = argparse.ArgumentParser(
            prog="shell",
            description="a shell for window managers with layer-shell protocol support",
        )

        parser.add_argument(
            "-i",
            "--instance-name",
            action="store",
            default="astal",
            help="Defaults to astal",
        )
        parser.add_argument(
            "-p",
            "--process-name",
            action="store",
            default="xtreme-shell",
            help="Defaults to xtreme-shell",
        )

        flags = parser.parse_args(args)

        setproctitle(flags.process_name)

    def add_if_enabled(self, window_class, *args):
        if hasattr(window_class, "is_enabled") is False:
            self.logger.warning(
                f"{window_class.__name__} does not have a 'is_enabled()' method"
            )
            return

        if window_class.is_enabled():
            self.add_window(window_class(*args))

    def __on_color_change(self):
        def finished(css):
            GLib.idle_add(self.apply_css, css, True)
            self.logger.info("Styles compiled")

        compile_scss(finished)

    def do_activate(self):
        Adw.init()
        init_logger()
        get_colors_watcher(self.__on_color_change)
        self.__on_color_change()

        self.add_if_enabled(Bar)
        CornerWindow.for_placements(lambda cls, x: self.add_if_enabled(cls, x))


def run(args):
    app = GtkShellApp()
    app.parse_args(args)
    app.acquire_socket()

    app.run()


if __name__ == "__main__":
    import sys

    run(sys.argv[1:])
