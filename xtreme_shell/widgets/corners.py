from gi.repository import Gtk, Astal
from xtreme_shell.modules.config import Corners as CornerConfig
from xtreme_shell.widgets.window import XtremeWindow
from enum import Enum
import logging
import cairo
import math


class Placement(Enum):
    TOP_LEFT = 1
    TOP_RIGHT = 2
    BOTTOM_LEFT = 3
    BOTTOM_RIGHT = 4


class Corner(Gtk.DrawingArea):
    def __init__(self, position, size=None):
        super().__init__(css_classes=["corner"])

        self.size = size
        self.position = position
        self.set_draw_func(self.do_draw)

    def do_draw(self, _, cr: cairo.Context, width: int, height: int):
        size = self.size or min(width, height)
        color = self.get_style_context().get_color()

        match self.position:
            case Placement.TOP_LEFT:
                cr.arc(size, size, size, math.pi, 3 * math.pi / 2)
                cr.line_to(0, 0)
            case Placement.TOP_RIGHT:
                cr.arc(0, size, size, 3 * math.pi / 2, 2 * math.pi)
                cr.line_to(size, 0)
            case Placement.BOTTOM_LEFT:
                cr.arc(size, 0, size, math.pi / 2, math.pi)
                cr.line_to(0, size)
            case Placement.BOTTOM_RIGHT:
                cr.arc(0, 0, size, 0, math.pi / 2)
                cr.line_to(size, size)

        cr.close_path()
        cr.set_source_rgba(color.red, color.green, color.blue, color.alpha)
        cr.fill()


class CornerWindow(XtremeWindow):
    def __init__(self, placement: Placement):
        super().__init__(
            "corner",
            "corner-" + placement.name,
            "top",
            placement.name.split("_"),
            css_classes=[],
            exclusivity=Astal.Exclusivity.EXCLUSIVE,
            with_background=False,
        )

        self.set_size_request(20, 20)
        self.set_child(Corner(placement, size=20))

        CornerConfig.opacity.on_change(self.__change_opacity)

        self.present()

    def __change_opacity(self, opacity):
        self.set_css(f"color: rgba(colors.$background, {opacity});")

    @staticmethod
    def is_enabled():
        return CornerConfig.enabled.value

    @classmethod
    def for_placements(cls, cb):
        corners = []
        for x in Placement:
            if x.name in CornerConfig.enabled_corners.value:
                cb(cls, x)
                corners.append(x.name)
        logging.getLogger("CornerWindow").info(f"Enabled corners: {corners}")
