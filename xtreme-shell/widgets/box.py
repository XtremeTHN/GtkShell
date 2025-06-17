from gi.repository import Gtk, GObject


class Box(Gtk.Box):
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
        super().__init__(
            orientation=Gtk.Orientation.VERTICAL
            if vertical
            else Gtk.Orientation.HORIZONTAL,
            spacing=spacing,
            css_classes=css_classes,
            **kwargs,
        )

        if len(children) > 0:
            self.append(*children)

    def append(self, *child):
        """
        Appends multiple :class:`Gtk.Widget` to the box.

        :param child: The :class:`Gtk.Widget` to append to the box
        """
        for x in child:
            super().append(x)
        # super().append(child)
