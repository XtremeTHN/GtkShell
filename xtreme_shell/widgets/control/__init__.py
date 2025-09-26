from gi.repository import Adw, Gtk, Gio, GLib, Astal, GObject
from xtreme_shell.modules.utils import Blp, get_signal_args
from .scripts import Scripts, ScriptItem

import threading
import logging


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


@Blp("control")
class ControlCenter(Astal.Window):
    __gtype_name__ = "ControlCenter"

    scripts_box: Gtk.ListBox = Gtk.Template.Child()

    def __init__(self):
        super().__init__(
            width_request=600,
            height_request=600,
            layer=Astal.Layer.OVERLAY,
        )
        self.logging = logging.getLogger("ControlCenter")
        self.scripts = Scripts()
        self.scripts.connect("script-added", self.on_script_added)

        self.add_css_class("adwaita-window")

        self.add_default_scripts()
        self.present()

    def on_script_added(self, _, nick):
        script_info = self.scripts.scripts[nick]

        s = ScriptItem()
        s.set_title(script_info["title"])
        s.set_subtitle(script_info["description"])

        s.script_target = nick

        self.scripts_box.append(s)

    def add_default_scripts(self):
        self.scripts.add_script(
            "winapps",
            {
                "title": "Start winapps",
                "description": "Starts the winapps container",
                "function": lambda: SimpleShellScript(
                    [
                        "podman-compose",
                        "--file",
                        f"/home/{GLib.get_user_name()}/Downloads/winapps/compose.yaml",  # TODO: make this configurable
                        "start",
                    ]
                ),
            },
        )
