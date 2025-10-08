from xtreme_shell.modules.utils import Blp
from gi.repository import Gtk, GLib, GObject
import time


def tween(start, end, duration, update_callback, done_callback=None):
    start_time = time.time()
    delta = end - start

    def _step():
        elapsed = time.time() - start_time
        progress = min(elapsed / duration, 1.0)
        current = start + delta * progress
        update_callback(current)
        if progress < 1.0:
            return True  # Continue
        else:
            if done_callback:
                done_callback()
            return False  # Stop

    GLib.idle_add(_step)


@Blp("quick-menu")
class QuickMenu(Gtk.Revealer):
    __gtype_name__ = "QuickMenu"

    icon: Gtk.Image = Gtk.Template.Child()
    root_box: Gtk.Image = Gtk.Template.Child()
    title_label: Gtk.Label = Gtk.Template.Child()

    @GObject.Property(type=str, nick="icon-name")
    def icon_name(self):
        return self.icon.get_icon_name()

    @icon_name.setter
    def icon_name(self, icon):
        self.icon.set_from_icon_name(icon)

    @GObject.Property(type=str)
    def title(self):
        return self.title_label.get_label()

    @title.setter
    def title(self, title):
        self.title_label.set_label(title)

    @GObject.Property(type=Gtk.Widget)
    def content(self):
        return

    @content.setter
    def content(self, content):
        self.root_box.append(content)

    def __init__(self):
        super().__init__()
        self.connect("notify::child-revealed", self.revealed)

    def revealed(self, *_):
        if self.get_reveal_child():
            tween(0, 1, 0.15, self.root_box.set_opacity)
        else:
            self.set_visible(False)

    def toggle(self, *_):
        orig = self.get_reveal_child()
        cond = not orig

        if cond:
            self.root_box.set_opacity(0)
            self.set_visible(True)
            self.set_reveal_child(cond)
        else:
            tween(
                1,
                0,
                0.15,
                self.root_box.set_opacity,
                lambda: self.set_reveal_child(cond),
            )
