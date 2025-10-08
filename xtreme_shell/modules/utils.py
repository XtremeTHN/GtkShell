from gi.repository import Gdk, Gtk, Gio, GObject, GLib
import logging


def notify(self, heading, body):
    app = self.get_root().get_application()
    notification = Gio.Notification.new(heading)
    notification.set_body(body)
    app.send_notification("script", notification)


def get_signal_args(flags="run-first", args=()):
    return (
        getattr(GObject.SignalFlags, flags.replace("-", "_").upper()),
        None,
        tuple(args),
    )


class Blp(Gtk.Template):
    def __init__(self, blp_name):
        super().__init__(
            resource_path=f"/com/github/XtremeTHN/XtremeShell/{blp_name}.ui"
        )


def to_button(widget, on_clicked):
    c = Gtk.GestureClick.new()
    c.set_button(0)
    c.connect("pressed", lambda *_: on_clicked(widget))

    widget.add_controller(c)


def box(vertical: bool, children=[], **kwargs):
    b = Gtk.Box(
        orientation=Gtk.Orientation.VERTICAL
        if vertical
        else Gtk.Orientation.HORIZONTAL,
        **kwargs,
    )

    for x in children:
        b.append(x)

    return b


def get_paintable_from_path(path) -> Gdk.Paintable | None:
    if path is None:
        return None
    try:
        txt = Gdk.Texture.new_from_filename(path)
        return txt
    except Exception:
        logging.getLogger("get_paintable_from_path").exception(
            f"Can't get paintable. Path: {path}"
        )
        return None
