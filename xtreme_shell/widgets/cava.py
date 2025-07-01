from gi.repository import Gtk, Gsk, AstalCava, AstalWp, GLib
from . import Widget


# ported from https://github.com/kotontrion/kompass/blob/main/libkompass/src/cava.vala
class Cava(Widget, Gtk.Widget):
    def __init__(self, active=False, stream=None):
        Gtk.Widget.__init__(self)
        Widget.__init__(self)

        self.cava = AstalCava.Cava.get_default()

        self.cava.connect("notify::values", lambda *_: self.queue_draw())
        self.connect("notify::visible", self.__on_visible_change)

        self.set_active(active)

        if stream:
            self.set_stream(stream)

    def set_active(self, active):
        self.cava.set_active(active)

    def set_stream(self, stream: AstalWp.Stream):
        self.cava.set_source(f"{stream.get_serial()}")

    def __on_visible_change(self, *_):
        self.set_active(self.get_visible())

    def __queue(self):
        if self.get_visible():
            self.queue_draw()
            return True
        else:
            return False

    def do_snapshot(self, snapshot):
        Gtk.Widget.do_snapshot(self, snapshot)

        width = self.get_width()
        height = self.get_height()
        color = self.get_color()

        values = self.cava.get_values()
        bars = self.cava.get_bars()

        if bars < 2 or len(values) < bars:
            return  # Not enough data to draw

        bar_width = width / (bars - 1)

        def y(idx):
            return height - height * values[idx]

        def x(idx):
            return idx * bar_width

        builder = Gsk.PathBuilder.new()
        builder.move_to(0, y(0))

        for i in range(bars - 1):
            # Calculate control points for smooth cubic interpolation
            if i == 0:
                p0 = (x(i), y(i))
                p3 = (x(i + 2), y(i + 2)) if i + 2 < bars else (x(i + 1), y(i + 1))
            elif i == bars - 2:
                p0 = (x(i - 1), y(i - 1))
                p3 = (x(i + 1), y(i + 1))
            else:
                p0 = (x(i - 1), y(i - 1))
                p3 = (x(i + 2), y(i + 2)) if i + 2 < bars else (x(i + 1), y(i + 1))

            p1 = (x(i), y(i))
            p2 = (x(i + 1), y(i + 1))

            # Cubic Bezier control points
            c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
            c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)

            builder.cubic_to(c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])

        # Close the path at the bottom
        builder.line_to(width, height)
        builder.line_to(0, height)
        builder.close()

        snapshot.append_fill(builder.to_path(), Gsk.FillRule.WINDING, color)
