import argparse

from .lib.versions import init

init()

from gi.repository import Astal, Gio  # noqa: E402

from .lib.config import Config  # noqa: E402
from .lib.loader import ModuleLoader
from .lib.constants import SOURCE_DIR, MODULES_DIR  # noqa: E402
from .lib.logger import getLogger  # noqa: E402
from .lib.style import Style  # noqa: E402
from .lib.task import Task  # noqa: E402
from .widgets.apps import ApplicationLauncher  # noqa: E402
from .widgets.bar import Bar  # noqa: E402
from .widgets.notifications import NotificationsWindow  # noqa: E402
from .widgets.notifications.center import NotificationCenter  # noqa: E402
from .widgets.quick.settings import QuickSettings  # noqa: E402


def get_from_list(index: int, _list):
    return _list[index] if len(_list) > index else None


class ShellApp(Astal.Application):
    def __init__(self, instance_name, start_only_modules):
        super().__init__(instance_name=instance_name)
        self.logger = getLogger("ShellApp")
        self.conf = Config.get_default()
        self.add_icons(str(SOURCE_DIR / "icons"))
        self.add_icons(str(MODULES_DIR / "icons"))
        self.start_only_modules = start_only_modules

    def do_astal_application_request(
        self, msg: str, conn: Gio.SocketConnection
    ) -> None:
        self.logger.info("Received a request: %s", msg)

    def reload(self, *_):
        self.logger.debug("Applying css...")
        self.apply_css(Style.compile_scss(), True)

    def add_if_enabled(self, window_class):
        if hasattr(window_class, "is_enabled") is False:
            self.logger.warning(
                f"implement is_enabled() for class {window_class.__name__}!"
            )
            return
        if window_class.is_enabled() is True:
            self.add_window(window_class())

    def add_module_windows(self):
        # Modules
        loader = ModuleLoader()
        modules = loader.load_from_config()
        for mod in modules:
            windows = mod.init(self)
            if windows is None or len(windows) == 0:
                self.logger.debug(f"Module {mod} didn't return any windows")
                continue
            else:
                for win in windows:
                    self.add_window(win)

    def do_activate(self) -> None:
        self.hold()
        self.reload()
        Style.watcher(self.reload)

        if self.start_only_modules is False:
            # Multi-monitor windows
            for m in self.get_monitors():
                self.add_window(Bar(m))

            # Single-monitor windows
            self.add_if_enabled(NotificationsWindow)
            self.add_if_enabled(NotificationCenter)
            self.add_if_enabled(ApplicationLauncher)
            self.add_if_enabled(QuickSettings)
            self.reload()

        self.add_module_windows()


def run(args):
    parser = argparse.ArgumentParser(prog="shell", description="Astal Gtk Shell")
    parser.add_argument("-i", "--instance", help="Instance name", default="astal")
    parser.add_argument("-p", "--procname", help="Process name", default="astal")
    parser.add_argument(
        "-m",
        "--start-only-modules",
        action="store_true",
        help="Only start modules windows",
        default=False,
    )
    args = parser.parse_args(args)

    app = ShellApp(args.instance, args.start_only_modules)
    if args.procname:
        from .lib.debug import set_proc_name

        set_proc_name(args.procname)

    app.acquire_socket()
    app.run()
    Task.stop_cancellable_tasks()


if __name__ == "__main__":
    run([])
