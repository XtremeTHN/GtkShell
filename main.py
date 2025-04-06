import lib.versions as _
import argparse

from gi.repository import Astal, AstalIO, Gio, Adw

from lib.task import Task
from lib.style import Style
from lib.config import Config
from lib.logger import getLogger
from lib.constants import CONFIG_DIR, SOURCE_DIR

from widgets.quick.settings import QuickSettings
from widgets.bar import Bar

Adw.init()


class ShellApp(Astal.Application):

    def __init__(self, instance_name):
        super().__init__(instance_name=instance_name)
        self.logger = getLogger("ShellApp")
        self.conf = Config.get_default()
        self.add_icons(str(SOURCE_DIR / "icons"))

    def do_astal_application_request(self, msg: str,
                                     conn: Gio.SocketConnection) -> None:
        self.logger.info("Received a request: %s", msg)

        args = msg.split(" ")

        if args[0] == "help":
            AstalIO.write_sock(conn, "Available commands:\n")

        if args[0] == "reload":
            self.logger.info("Reloading css...")
            self.reload()

    def reload(self, *_):
        self.logger.debug("Applying css...")
        Style.compile_scss()
        self.apply_css(str(CONFIG_DIR / "style/style.css"), True)

    def do_activate(self) -> None:
        self.hold()
        self.reload()

        Style.watcher(self.reload)
        for m in self.get_monitors():
            self.add_window(Bar(m))
            self.add_window(QuickSettings(m))


def run(args):
    parser = argparse.ArgumentParser(prog="gtk-shell",
                                     description="Astal Gtk Shell")
    parser.add_argument("-i",
                        "--instance",
                        help="Instance name",
                        default="astal")
    parser.add_argument("-p",
                        "--procname",
                        help="Process name",
                        default="astal")
    args = parser.parse_args(args)

    app = ShellApp(args.instance)
    if args.procname:
        from lib.debug import set_proc_name
        set_proc_name(args.procname)

    app.acquire_socket()
    app.run()
    Task.stop_cancellable_tasks()


if __name__ == "__main__":
    run([])
