from gi.repository import GObject, Gtk

from .box import Box


class QuickButton(Box):
    __gsignals__ = {
        "activated": (GObject.SIGNAL_RUN_FIRST, None, tuple()),
        "deactivated": (GObject.SIGNAL_RUN_FIRST, None, tuple()),
        "menu-toggled": (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        "add-widget": (GObject.SIGNAL_RUN_FIRST, None, (Gtk.ScrolledWindow, str)),
    }

    def __init__(self, icon, header, default_subtitle, has_menu=True):
        """
        Creates a QuickButton widget.

        :param icon: A Gtk.Image widget to be used as the icon on the QuickButton.
        :type icon: Gtk.Image
        :param header: A string to be used as the header of the QuickButton.
        :type header: str
        :param default_subtitle: A string to be used as the default subtitle of the QuickButton.
        :type default_subtitle: str
        """
        super().__init__(vertical=True)

        self.active = False
        self.stack: Gtk.Stack = None
        self.menu = None
        self.menu_id = None

        self.overlay = Gtk.Overlay.new()
        self.button = Gtk.Button(css_classes=["quickbutton", "toggle-button"])

        self.button_content = Box(spacing=10)
        self._label_box = Box(spacing=0, vertical=True)
        self.heading = Gtk.Label(
            label=header, xalign=0, css_classes=["quickbutton-heading"]
        )
        self.subtitle = Gtk.Label(
            label=default_subtitle, xalign=0, css_classes=["quickbutton-subtitle"]
        )

        self._label_box.append_all([self.heading, self.subtitle])
        self.button_content.append_all([icon, self._label_box])

        self.button.set_child(self.button_content)

        self.overlay.set_child(self.button)
        if has_menu:
            self.right_button = Gtk.Button(
                css_classes=["quickbutton-right"],
                halign=Gtk.Align.END,
                icon_name="go-next-symbolic",
            )

            self.right_button.connect("clicked", self.toggle_menu)

            self.overlay.add_overlay(self.right_button)
            self.overlay.set_measure_overlay(self.right_button, True)

        self.button.connect("clicked", self.__on_click)

        self.append(self.overlay)

    def set_stack(self, stack):
        self.stack = stack
        if self.menu is not None:
            self.stack.add_named(self.menu, self.menu_id)

    def set_menu(self, menu, menu_id):
        self.menu = menu
        menu.back_btt.connect("clicked", self.toggle_menu)
        self.menu_id = menu_id

    def toggle_menu(self, *_):
        if self.menu_id is None:
            return
        if self.stack.get_visible_child_name() == self.menu_id:
            self.stack.set_visible_child_name("main")
        else:
            self.stack.set_visible_child_name(self.menu_id)

    def __on_click(self, _):
        self.set_active(not self.active)

    def set_active(self, active):
        if active is True:
            self.active = True
            self.emit("activated")
            self.button.add_css_class("active")
        else:
            self.active = False
            self.emit("deactivated")
            self.button.remove_css_class("active")


class QuickUtilButton(QuickButton):
    def __init__(
        self,
        icon,
        header,
        default_subtitle,
        object,
        watch_property,
        has_menu=True,
        cb=None,
    ):
        super().__init__(icon, header, default_subtitle, has_menu=has_menu)
        cb = cb or self.__on_change

        self.object: GObject.GObject = object
        self.watch_property = watch_property

        self.object.connect(f"notify::{watch_property}", cb or self.__on_change)
        cb()

    def __on_change(self, *_):
        prop = len(self.object.get_property(self.watch_property))
        if prop == 0:
            self.subtitle.set_text("No applications")
        else:
            self.subtitle.set_text(
                "1 application" if prop == 1 else f"{prop} applications"
            )
