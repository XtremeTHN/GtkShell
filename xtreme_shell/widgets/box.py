from gi.repository import Gtk
from . import Widget


class Box(Gtk.Box, Widget):
    def __init__(
        self, vertical=False, spacing=0, children=[], css_classes=[], **kwargs
    ):
        """
        Helper class for :class:`Gtk.Box`

        :param vertical: If True, the box will be vertical. Otherwise horizontal.
        :param spacing: The spacing between each child.
        :param children: An iterable of :class:`Gtk.Widget` to append to the box.
        :param css_classes: A list of CSS classes to apply to the box.
        """

        Gtk.Box.__init__(
            self,
            orientation=Gtk.Orientation.VERTICAL
            if vertical
            else Gtk.Orientation.HORIZONTAL,
            spacing=spacing,
            css_classes=css_classes,
            **kwargs,
        )
        Widget.__init__(self)

        if len(children) > 0:
            self.append(*children)

    def append(self, *child):
        """
        Appends multiple :class:`Gtk.Widget` to the box.

        :param child: The :class:`Gtk.Widget` to append to the box
        """
        for x in child:
            super().append(x)
