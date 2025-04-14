from lib.utils import lookup_icon, get_signal_args
from gi.repository import Gtk, Adw, AstalNotifd, Pango
from widgets.custom.box import Box


class Header(Box):

    def __init__(self, notif):
        super().__init__(css_classes=["header"], vertical=True)
        control = Box()
        self.title_widget = Gtk.Label(label=notif.get_app_name(),
                                      xalign=0,
                                      css_classes=["dimmed"],
                                      hexpand=True)
        self.close_btt = Gtk.Button(icon_name="window-close-symbolic",
                                    vexpand=False,
                                    css_classes=["flat"])
        control.append_all([self.title_widget, self.close_btt])
        self.append(control)

        sep = Gtk.Separator()
        self.append(sep)


class NotifAction(Gtk.Button):

    def __init__(self, action: AstalNotifd.Action):
        super().__init__()
        content = Box()

        self.label = Gtk.Label(label=action.label)
        self.id = action.id

        content.append(self.label)
        self.set_child(content)


class Notification(Adw.Bin):
    __gsignals__ = {
        "dismiss":
        get_signal_args("run-last", args=(int, AstalNotifd.ClosedReason))
    }

    def __init__(self, notif: AstalNotifd.Notification):
        super().__init__(css_classes=["card", "notification"], margin_end=20)

        #self.toolbar = Adw.ToolbarView()
        v_cont = Box(vertical=True, spacing=10)

        h_cont = Box(spacing=15)
        self.header = Header(notif)
        self.image = Gtk.Image()

        labels_box = Box(vertical=True)
        self.title = Gtk.Label(label=notif.get_summary(),
                               xalign=0,
                               use_markup=True,
                               css_classes=["title-2"])
        self.body = Gtk.Label(label=notif.get_body(),
                              xalign=True,
                              hexpand=True,
                              vexpand=True,
                              wrap=True,
                              wrap_mode=Pango.WrapMode.CHAR,
                              use_markup=True,
                              max_width_chars=70)

        #self.toolbar.add_top_bar(self.header)
        v_cont.append(self.header)
        labels_box.append_all([self.title, self.body])

        img = notif.get_image()
        if img is not None:
            if lookup_icon(img) is False:
                self.image.set_from_file(img)
            else:
                self.image.set_from_icon_name(img)
            h_cont.append(self.image)
        h_cont.append(
            Adw.Clamp(child=labels_box,
                      maximum_size=300,
                      halign=Gtk.Align.START))

        v_cont.append(h_cont)

        actions = notif.get_actions()
        if len(actions) > 0:
            actions_box = Box(spacing=5)
            actions_box.append_all(
                [NotifAction(a) for a in actions],
                map_func=lambda x: x.connect("clicked", self.__invoke, notif))
            v_cont.append(actions_box)

        #self.toolbar.set_content(v_cont)

        self.set_child(v_cont)

        self.header.close_btt.connect("clicked", self.__close, notif)

    def __invoke(self, btt: NotifAction, notif):
        notif.invoke(btt.id)

    def __close(self, _, notif):
        self.emit("dismiss", notif.get_id(),
                  AstalNotifd.ClosedReason.DISMISSED_BY_USER)
