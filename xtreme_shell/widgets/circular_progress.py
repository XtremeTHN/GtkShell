from gi.repository import Adw, Gtk, GObject, Graphene, Gdk, GLib


class CircularProgress(GObject.Object, Gdk.Paintable, Gtk.SymbolicPaintable):
    __gtype_name__ = "CircularProgress"

    def __init__(self):
        super().__init__()

        self.__progress = 0.0
        self.__widget = None

    @GObject.Property(type=Gtk.Widget)
    def widget(self):
        return self.__widget

    @widget.setter
    def widget(self, value):
        self.__widget = value
        value.connect("notify::scale-factor", self.on_scale_change)

    @GObject.Property(type=float)
    def progress(self):
        return self.__progress

    @progress.setter
    def progress(self, value):
        if value > 1:
            value = 1
        if value < 0:
            value = 0

        self.__progress = value
        self.invalidate_contents()

    def do_snapshot_symbolic(self, snapshot: Gtk.Snapshot, width, height, colors, _):
        ctx = snapshot.append_cairo(Graphene.Rect().init(-2, -2, width + 4, width + 4))
        arc_end = self.progress * GLib.PI * 2 - GLib.PI / 2

        ctx.translate(width / 2.0, height / 2.0)

        color = colors[0]
        ctx.set_source_rgba(color.red, color.green, color.blue, color.alpha)

        ctx.arc(0, 0, width / 2.0 + 1, -GLib.PI / 2, arc_end)
        ctx.stroke()

        rgba = color.copy()
        rgba.alpha *= 0.25

        ctx.set_source_rgba(rgba.red, rgba.green, rgba.blue, rgba.alpha)
        ctx.arc(0, 0, width / 2.0 + 1, arc_end, 3.0 * GLib.PI / 2.0)
        ctx.stroke()

    def get_intrinsic_height(self):
        return 16 * self.widget.get_scale_factor()

    def get_intrinsic_width(self):
        return 16 * self.widget.get_scale_factor()

    def on_scale_change(self, *_):
        self.invalidate_size()
