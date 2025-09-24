from gi.repository import AstalNotifd, Astal, Gtk, Pango
from xtreme_shell.modules.utils import get_paintable_from_path


def box(vertical: bool, children=[], **kwargs):
    b = Gtk.Box(
        orientation=Gtk.Orientation.VERTICAL
        if vertical
        else Gtk.Orientation.HORIZONTAL,
        **kwargs,
    )

    for x in children:
        b.append(x)

    return b


class Notification(Gtk.ListBoxRow):
    def __init__(self, notif: AstalNotifd.Notification):
        super().__init__(width_request=300)
        self.notif = notif

        self.setup_widgets()

    def action_callback(self, button):
        self.notif.invoke(button.id)
        # self.notif.dismiss()

    def build_button(self, action: AstalNotifd.Action):
        b = Gtk.Button()
        b.id = action.id

        if self.notif.get_action_icons():
            b.set_icon_name(action.id)
        else:
            b.set_label(action.label)

        b.connect("clicked", self.action_callback)

        return b

    def setup_widgets(self):
        root = box(True, spacing=10)
        self.set_child(root)

        header = Gtk.CenterBox.new()
        root.append(header)

        icon = Gtk.Image(
            icon_name=self.notif.get_app_icon() or "application-x-executable-symbolic",
            opacity=0.6,
        )

        title = Gtk.Label(
            label=self.notif.get_app_name() or "Unknown application", opacity=0.6
        )

        left = box(False, children=[icon, title], spacing=10)

        header.set_start_widget(left)

        notification_image = Gtk.Image(pixel_size=64)
        if (paintable := get_paintable_from_path(self.notif.get_image())) is not None:
            notification_image.set_paintable(paintable)
        else:
            notification_image.set_visible(False)

        summary = Gtk.Label(
            label=self.notif.get_summary(), xalign=0, css_classes=["heading"]
        )
        body = Gtk.Label(
            label=self.notif.get_body(),
            xalign=0,
            wrap=True,
            wrap_mode=Pango.WrapMode.WORD_CHAR,
        )

        texts = box(True, children=[summary, body], spacing=5)

        center = box(False, children=[notification_image, texts], spacing=10)
        root.append(center)

        actions = box(
            False,
            children=[self.build_button(x) for x in self.notif.props.actions],
            spacing=5,
        )
        revealer = Gtk.Revealer(
            transition_type=Gtk.RevealerTransitionType.SLIDE_DOWN,
            transition_duration=200,
            child=actions,
        )
        root.append(revealer)


class Notifications(Astal.Window):
    notif_list: Gtk.ListBox

    def __init__(self):
        super().__init__(
            name="notifications",
            namespace="shell-notifications",
            anchor=Astal.WindowAnchor.TOP | Astal.WindowAnchor.RIGHT,
            layer=Astal.Layer.OVERLAY,
            margin_end=10,
            css_classes=[],
        )

        self.notifd = AstalNotifd.get_default()
        self.notifd.connect("notified", self.on_notified)

        self.setup_widgets()
        self.present()

    def on_notified(self, _, id: int, replaced: bool):
        notif = self.notifd.get_notification(id)
        self.notif_list.append(Notification(notif))

    def setup_widgets(self):
        self.notif_list = Gtk.ListBox(css_classes=["boxed-list-separate", "notif-list"])
        self.set_child(self.notif_list)

        for x in self.notifd.props.notifications:
            self.notif_list.append(Notification(x))
