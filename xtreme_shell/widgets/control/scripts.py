from gi.repository import Gtk, Adw, GObject, Gio, GLib
from xtreme_shell.modules.utils import Blp, get_signal_args
import logging


class Scripts(GObject.Object):
    instance = None
    scripts: dict[str, dict] = {}

    __gsignals__ = {"script-added": get_signal_args(args=[str])}

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        super().__init__()

    def add_script(self, nickname: str, data: dict):
        self.scripts[nickname] = data
        self.emit("script-added", nickname)

    def check_if_running(self, proc: str):
        p = Gio.Subprocess.new(["pgrep", proc], Gio.SubprocessFlags.STDOUT_SILENCE)
        return p.wait_check(None)


class SimpleShellScript(GObject.Object):
    __gsignals__ = {"finish": get_signal_args(args=[bool, GLib.Bytes, GLib.Bytes])}

    def __init__(self, args):
        super().__init__()

        self.cancellable = Gio.Cancellable.new()
        self.proc = Gio.Subprocess.new(args, Gio.SubprocessFlags.NONE)

        self.proc.communicate_async(
            stdin_buf=None, cancellable=self.cancellable, callback=self.on_proc_finish
        )

    def on_proc_finish(self, _, res):
        no_error, stdout, stderr = self.proc.communicate_finish(res)
        self.emit("finish", no_error, stdout, stderr)


@Blp("script-item")
class ScriptItem(Adw.ActionRow):
    __gtype_name__ = "ScriptItem"

    stack: Gtk.Stack = Gtk.Template.Child()
    run_button: Gtk.Button = Gtk.Template.Child()

    script_target = GObject.Property(type=str, nick="script-target")

    def __init__(self):
        super().__init__()
        self.logging = logging.getLogger("ScriptItem")
        self.scripts = Scripts()

    @Gtk.Template.Callback()
    def start_script(self, _):
        def on_finish(*_):
            self.run_button.set_sensitive(True)
            self.stack.set_visible_child_name("icon")

        data = self.scripts.scripts[self.script_target]

        if self.scripts.check_if_running("windows"):
            notification = Gio.Notification.new("Scripts")
            notification.set_body(f"{data['title']} is already running")
            a: Adw.Application = self.get_root().get_application()
            a.send_notification("script", notification)
            return

        self.run_button.set_sensitive(False)
        self.stack.set_visible_child_name("running")
        data["function"]().connect("finish", on_finish)
