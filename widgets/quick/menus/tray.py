from gi.repository import Gtk, AstalTray
from lib.utils import getLogger, Box

_tray = AstalTray.get_default()

class QuickAppTray(Gtk.Button):
    def __init__(self, item_id):
        super().__init__()
        self.item = self.tray.get_item(item_id)

class QuickSysTrayMenu(Box):
    def __init__(self):
        super().__init__(vertical=True, spacing=0)
        self.logger = getLogger("QuickSysTrayMenu")
        self.tray = AstalTray.get_default()

        self.items = {}

        self.tray.connect("item-added", self.__on_item_added)
        self.tray.connect("item-removed", self.__on_item_removed)
    
    def __on_item_added(self, _, item_id):
        self.items[item_id] = 
    
    def __on_item_removed(self, _, item_id):
        self.items.pop(item_id)