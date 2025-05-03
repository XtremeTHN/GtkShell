from gi.repository import GObject, Gtk

from lib.utils import getLogger
from widgets.custom.widget import CustomizableWidget


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
        self.__children = []
        self.append_all(children)

    @GObject.Property()
    def children(self):
        return self.__children

    @children.setter
    def children(self, value):
        self.__children = value
        self.clear()
        self.append_all(value)
        self.notify("children")

    def clear(self):
        while (w := self.get_last_child()) is not None:
            self.remove(w)

    def append_all(self, children, map_func=None):
        """
        Appends all elements of `children` to the box.

        :param children: An iterable of :class:`Gtk.Widget` to append to the box
        """
        for c in children:
            if map_func is not None:
                map_func(c)
            self.append(c)

    def append(self, child):
        """
        Appends a single :class:`Gtk.Widget` to the box.

        :param child: The :class:`Gtk.Widget` to append to the box
        """
        super().append(child)
        self.__children.append(child)
        self.notify("children")

    def remove(self, widget):
        """
        Removes a specified :class:`Gtk.Widget` from the box.

        :param widget: The :class:`Gtk.Widget` to remove from the box
        """
        super().remove(widget)
        self.__children.pop(self.__children.index(widget))
        self.notify("children")


class StatusPage(Box):
    def __init__(self, title=None, description=None, icon=None):
        super().__init__(vertical=True, vexpand=True, valign=Gtk.Align.CENTER)
        self.__title = Gtk.Label(label=title, css_classes=["title-3"])
        self.__description = Gtk.Label(label=description, css_classes=["dimmed"])
        self.__icon = Gtk.Image(
            icon_name=icon, pixel_size=28, margin_bottom=10, css_classes=["dimmed"]
        )

        self.append_all([self.__icon, self.__title, self.__description])

    def set_title(self, title):
        self.__title.set_label(title)

    def set_description(self, desc):
        self.__description.set_label(desc)

    def set_icon_name(self, icon_name):
        self.__icon.set_from_icon_name(icon_name)


class QuickPage(Box):
    stack: Gtk.Stack = None

    def __init__(self, title: str, max_height=250):
        super().__init__(spacing=10, vertical=True)
        self.max_height = max_height
        self.__top = Box(spacing=10)

        self.back_btt = Gtk.Button(
            icon_name="go-previous-symbolic", css_classes=["circular"]
        )
        self.__title = Gtk.Label(label=title, css_classes=["title-3"])

        self.__top.append_all([self.back_btt, self.__title])
        self.append(self.__top)

    def set_child(self, child):
        self.append(
            Gtk.ScrolledWindow(
                css_classes=["box-10", "card"],
                child=child,
                vexpand=True,
                max_content_height=self.max_height,
            )
        )

    def pack_end(self, child):
        child.set_halign(Gtk.Align.END)
        self.__top.append(child)


class QuickMenu(Box):
    def __init__(
        self, title: str, max_height=150, show_top_bar=True, logger_name="QuickMenu"
    ):
        super().__init__(vertical=True, spacing=10)
        self.logger = getLogger(logger_name)
        self.max_height = max_height
        if show_top_bar:
            self.__top = Box(spacing=10, hexpand=True)
            self.back_btt = Gtk.Button(
                icon_name="go-previous-symbolic", css_classes=["circular"]
            )
            self.__title = Gtk.Label(label=title, css_classes=["title-3"])
            self.__top_end = Box(spacing=10, hexpand=True, halign=Gtk.Align.END)
            self.__top.append_all([self.back_btt, self.__title, self.__top_end])
            self.append(self.__top)

        self.scroll = Gtk.ScrolledWindow(
            css_classes=["box-10", "card"], vexpand=True, max_content_height=max_height
        )
        self.content = Box(spacing=4, vertical=True, vexpand=True)
        self.__placeholder = StatusPage()

        self.scroll.set_child(self.content)

        self.content.append(self.__placeholder)
        self.append(self.scroll)

        self.content.connect("notify::children", self.on_children_change)
        self.on_children_change()

        self.append_all = self.content.append_all
        self.append = self.content.append
        self.remove = self.content.remove
        self.clear = self.content.clear

    def on_children_change(self, *_):
        if len(self.content.children) == 1:
            self.__placeholder.set_visible(True)
        else:
            self.__placeholder.set_visible(False)

    def set_placeholder_attrs(self, title, description, icon_name, visible=True):
        self.__placeholder.set_title(title)
        self.__placeholder.set_description(description)
        self.__placeholder.set_icon_name(icon_name)
        self.__placeholder.set_visible(visible)

    def set_placeholder_visibility(self, visible):
        self.__placeholder.set_visible(visible)

    def set_placeholder_title(self, title):
        self.__placeholder.set_title(title)

    def set_placeholder_description(self, description):
        self.__placeholder.set_description(description)

    def set_placeholder_icon_name(self, icon_name):
        self.__placeholder.set_icon_name(icon_name)

    def titlebar_pack_end(self, child):
        child.set_halign(Gtk.Align.END)
        self.__top_end.append(child)


class ColoredBox(Box, CustomizableWidget):
    def __init__(self, color: str, **kwargs):
        """
        A box with a background color.
        :param color: The background color of the box. Use the namespace colors for accessing matugen-generated colors.
        """
        Box.__init__(self, **kwargs)
        CustomizableWidget.__init__(self)
        self.set_css(f"background-color: {color};")
