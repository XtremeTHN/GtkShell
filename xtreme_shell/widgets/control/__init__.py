from gi.repository import Gtk, GLib, Astal
from xtreme_shell.modules.utils import Blp
from .scripts import Scripts, ScriptItem, SimpleShellScript
import logging


@Blp("control")
class ControlCenter(Astal.Window):
    __gtype_name__ = "ControlCenter"

    scripts_box: Gtk.ListBox = Gtk.Template.Child()

    def __init__(self):
        super().__init__(
            name="control",
            namespace="shell-control",
            width_request=600,
            height_request=600,
            layer=Astal.Layer.OVERLAY,
            hide_on_close=True,
        )
        self.logging = logging.getLogger("ControlCenter")
        self.scripts = Scripts()
        self.scripts.connect("script-added", self.on_script_added)

        self.add_css_class("adwaita-window")

        self.add_default_scripts()
        self.present()

        self.set_visible(False)

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
                "process": "windows",
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
