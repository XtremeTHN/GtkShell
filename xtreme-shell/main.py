from gi.repository import Astal, AstalIO, Gtk
from modules.logger import init_logger
from setproctitle import setproctitle
import argparse


class GtkShellApp(Astal.Application):
    def __init__(self):
        super().__init__(application_id="com.github.XtremeTHN.GtkShell")

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

        self.set_instance_name(flags.instance_name)
        setproctitle(flags.process_name)

    def do_activate(self):
        self.hold()
        init_logger()


def run(args):
    app = GtkShellApp()
    app.parse_args(args)

    app.run()


if __name__ == "__main__":
    import sys

    run(sys.argv[1:])
