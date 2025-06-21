from gi.repository import Astal, Gtk, Gtk4LayerShell
from xtreme_shell.modules.services.opt import opt
from . import Widget
from typing import Literal


Layers = Literal[
    "background",
    "overlay",
    "bottom",
    "top",
]
Anchors = Literal["top", "right", "bottom", "left"]


class XtremeWindow(Astal.Window, Widget):
    def __init__(
        self, namespace, name, layer: Layers, anchors: list[Anchors], **kwargs
    ):
        Widget.__init__(self)
        Astal.Window.__init__(
            self,
            namespace=namespace,
            name=name,
            layer=getattr(Astal.Layer, layer.upper()),
            **kwargs,
        )

        self.__change_opacity(1)
        self.set_anchor(anchors)

    def __change_opacity(self, opacity):
        self.set_css(f"background-opacity: rgba(c.$background, {opacity};")
    
    def set_opacity_option(self, option: opt):
        option.on_change(self.__change_opacity)

    def set_anchor(self, anchors: list[str]):
        length = len(anchors)
        if length > 4:
            anchors = anchors[:3]
        for anchor in anchors:
            anchor_obj = getattr(Gtk4LayerShell.Edge, anchor.upper(), None)
            if anchor_obj is not None:
                Gtk4LayerShell.set_anchor(self, anchor_obj, True)
            else:
                self.logger.warning(f"Invalid anchor: '{anchor}'")
