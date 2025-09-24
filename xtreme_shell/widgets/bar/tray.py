from gi.repository import AstalTray, Gtk, GObject


class Item(Gtk.Image):
    def __init__(self, item: AstalTray.TrayItem):
        super().__init__()

        self.popover = Gtk.PopoverMenu.new_from_model(item.get_menu_model())

        cont = Gtk.GestureClick.new()
        cont.set_button(3)
        cont.connect("released", self.show_menu)

        item.bind_property("gicon", self, "gicon", GObject.BindingFlags.SYNC_CREATE)

        item.connect(
            "notify::action-group",
            lambda *_: self.popover.insert_action_group(
                "dbusmenu", item.get_action_group()
            ),
        )

        self.popover.set_parent(self)
        self.add_controller(cont)

    def show_menu(self, controller: Gtk.GestureClick, *_):
        self.popover.popup()


class Tray(Gtk.Box):
    def __init__(self):
        super().__init__(spacing=10)

        self.widgets = {}
        self.tray = AstalTray.get_default()

        self.tray.connect("item-added", self.item_added)
        self.tray.connect("item-removed", self.item_removed)

    def item_added(self, _, index):
        item = Item(self.tray.get_item(index))

        self.widgets[index] = item
        self.append(item)

    def item_removed(self, _, index):
        self.remove(self.widgets.pop(index))
