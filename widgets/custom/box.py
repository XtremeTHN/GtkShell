from gi.repository import Gtk, GObject
from lib.utils import getLogger

class Box(Gtk.Box):
    def __init__(self, vertical=False, spacing=0, children=[], css_classes=[], **kwargs):
        """
        Helper class for :class:`Gtk.Box`
        
        :param vertical: If True, the box will be vertical. Otherwise horizontal.
        :param spacing: The spacing between each child.
        :param children: An iterable of :class:`Gtk.Widget` to append to the box.
        :param css_classes: A list of CSS classes to apply to the box.
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL if vertical else Gtk.Orientation.HORIZONTAL, spacing=spacing, css_classes=css_classes, **kwargs)
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
        while (w:=self.get_last_child()) is not None:
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
        self.__icon = Gtk.Image(icon_name=icon, pixel_size=28, margin_bottom=10, css_classes=["dimmed"])

        self.append_all([self.__icon, self.__title, self.__description])
    
    def set_title(self, title):
        self.__title.set_label(title)
    
    def set_description(self, desc):
        self.__description.set_label(desc)
    
    def set_icon_name(self, icon_name):
        self.__icon.set_from_icon_name(icon_name)
    
class QuickMenu(Box):
    def __init__(self, logger_name="QuickMenu"):
        super().__init__(vertical=True, spacing=4)
        self.logger = getLogger(logger_name)

        self.__placeholder = StatusPage()
        self.connect("notify::children", self.on_children_change); self.on_children_change()
        self.append(self.__placeholder)

    def on_children_change(self, *_):
        if len(self.children) == 1:
            self.__placeholder.set_visible(True)
        else:
            self.__placeholder.set_visible(False)

    def set_placeholder_attrs(self, title, description, icon_name, visible=True):
        self.__placeholder.set_title(title)
        self.__placeholder.set_description(description)
        self.__placeholder.set_icon_name(icon_name)
        self.__placeholder.set_visible(visible)
    
    def set_placeholder_visibility(self, visible):
        self.logger.debug(f"Setting placeholder visibility to {visible}")
        self.__placeholder.set_visible(visible)
    
    def set_placeholder_title(self, title):
        self.__placeholder.set_title(title)
    
    def set_placeholder_description(self, description):
        self.__placeholder.set_description(description)
    
    def set_placeholder_icon_name(self, icon_name):
        self.__placeholder.set_icon_name(icon_name)