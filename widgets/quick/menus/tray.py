from gi.repository import Gtk, AstalTray
from lib.utils import getLogger, Box

_tray = AstalTray.get_default()

class QuickAppTray(Box):
    def __init__(self, item_id):
        self.item = _tray.get_item(item_id)
        super().__init__(spacing=10, css_classes=["false-button"])

        self.icon = Gtk.Image(icon_name=self.item.props.icon_name, pixel_size=24)
        self.menu = Gtk.PopoverMenu()
        self.description = Gtk.Label(label=self.item.props.title.title())
        self.gesture = Gtk.GestureSingle(button=0)

        self.item.connect("notify::menu-model", self.__new_menu); self.__new_menu()
        self.item.connect("notify::action-group", self.__new_menu)
        self.item.connect("notify::tooltip", self.__change_tooltip); self.__change_tooltip()

        self.gesture.connect("begin", self.__prepare)
        self.gesture.connect("end", self.__show)
        
        self.add_controller(self.gesture)
        # like Gtk.MenuButton.set_popover func
        self.menu.set_parent(self)
        self.icon.set_tooltip_markup(self.item.props.tooltip_markup)
        self.append_all([self.icon, self.description])
    
    def __show(self, _, __):
        if self.gesture.get_current_button() == 1:
            self.item.activate(0,0)
        elif self.gesture.get_current_button() == 3:
            self.menu.popup()

    def __change_tooltip(self, *_):
        if self.item.props.tooltip is not None:
            self.icon.set_tooltip_text(self.item.props.tooltip.description)
    
    def __prepare(self, *_):
        self.item.about_to_show()

    def __new_menu(self, *_):
        self.menu.set_menu_model(self.item.props.menu_model)
        self.menu.insert_action_group("dbusmenu", self.item.props.action_group)

class QuickSysTrayMenu(Box):
    def __init__(self):
        super().__init__(vertical=True, spacing=0)
        self.logger = getLogger("QuickSysTrayMenu")
        self.tray = AstalTray.get_default()

        self.items = {}

        self.tray.connect("item-added", self.__on_item_added)
        self.tray.connect("item-removed", self.__on_item_removed)
    
    def __on_item_added(self, _, item_id):
        item = QuickAppTray(item_id)
        self.items[item_id] = item
        self.append(item)
    
    def __on_item_removed(self, _, item_id):
        self.remove(self.items.pop(item_id))