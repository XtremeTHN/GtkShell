from typing import TypeVar

from gi.repository import Gio, GLib, GObject, Gtk
from inotify.adapters import Inotify
from inotify.constants import IN_MODIFY

from .logger import getLogger
from .task import Task


class Watcher(GObject.Object, Task):
    __gsignals__ = {"event": (GObject.SignalFlags.RUN_FIRST, None, (str,))}

    def __init__(self):
        self.logger = getLogger("Watcher")
        self._name = "Watcher"
        GObject.Object.__init__(self)
        Task.__init__(self, self.__run)

        self.cancellable = Gio.Cancellable.new()
        self.watcher = Inotify()

    def add_watch(self, path, mask=IN_MODIFY):
        try:
            self.watcher.add_watch(path, mask=mask)
        except Exception:
            self.logger.exception("Failed to add watch for %s", path)
            return
        self._name = path

    def stop(self):
        self.cancellable.cancel()

    def __run(self):
        for event in self.watcher.event_gen():
            if self.cancellable.is_cancelled():
                break

            if event is not None:
                self.emit("event", event[1][0])


T = TypeVar("T", bound="Object")


class Object(GObject.Object):
    _instance = None

    def __init__(self):
        super().__init__()

    @classmethod
    def get_default(cls: type[T]) -> T:
        """
        Returns the default Service object for this process, creating it if necessary.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


class Timeout:
    def __init__(self, func, delay, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        GLib.timeout_add(delay, self.__run)

    def __run(self):
        if (n := self.func(*self.args, **self.kwargs)) is not None:
            return n
        return GLib.SOURCE_REMOVE


def notify(title, message, log=True):
    if log:
        getLogger("notify").info("[%s] %s", title, message)
    GLib.spawn_command_line_async(f"notify-send '{title}' '{message}'")


def get_signal_args(flags, args=()):
    return (
        getattr(GObject.SignalFlags, flags.replace("-", "_").upper()),
        None,
        tuple(args),
    )


def lookup_icon(name: str):
    return Gtk.IconTheme().has_icon(name)
