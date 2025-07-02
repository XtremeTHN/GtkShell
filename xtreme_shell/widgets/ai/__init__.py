from xtreme_shell.modules.constants import SOURCE_DIR
from xtreme_shell.widgets.window import XtremeWindow
from xtreme_shell.widgets.box import Box
from gi.repository import Gtk, Adw


class Gemini(XtremeWindow):
    def __init__(self):
        super().__init__("gemini", "astal-gemini-bar", "top", ["bottom"])

    def setup_widgets(self):
        content = Box(vertical=True, spacing=0)

        icon = Gtk.Image.new_from_file(str(SOURCE_DIR / "icons"))
        popmenu = Gtk.MenuButton(css_classes=["circular"], child=icon)

        label = Gtk.Label(label="Ask gemini...", css_classes=["dimmed"])
