from gi.repository import Gtk, Adw, AstalNotifd
from widgets.custom.box import Box
from lib.utils import lookup_icon


def get_header(title):
    h = Adw.HeaderBar.new()
    t = Gtk.Label(label=title, css_classes=["dimmed", "title-3"])
    h.pack_start(title)

    return h

class NotifAction(Gtk.Button):

    def __init__(self, action: AstalNotifd.Action):
        super().__init__()
        content = Box()

        self.label = Gtk.Label(label=action.label)
        self.id = action.id

        content.append(self.label)
        self.set_child(content)


class Notification(Adw.ToolbarView):

    def __init__(self, notif: AstalNotifd.Notification):
        super().__init__()
        v_cont = Box(vertical=True, spacing=5)

        h_cont = Box(spacing=15)
        self.header = get_header(notif.get_app_name())
        self.image = Gtk.Image()
        img = notif.get_image()
        if lookup_icon(img) is False:
            self.image.set_from_file(img)
        else:
            self.image.set_from_icon_name(img)

        labels_box = Box(vertical=True)
        self.title = Gtk.Label(label=notif.get_summary(),
                               css_classes=["title-2"])
        self.body = Gtk.Label(label=notif.get_body(), vexpand=True)

        self.add_top_bar(self.header)
        labels_box.append_all([self.title, self.body])

        h_cont.append(self.image)
        h_cont.append(labels_box)

        v_cont.append(h_cont)

        actions = notif.get_actions()
        if len(actions) > 0:
            actions_box = Box(spacing=5)
            actions_box.append_all([NotifAction(a) for a in actions])
            v_cont.append(actions_box)

        self.set_content(v_cont)
