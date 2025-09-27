from gi.repository import AstalNotifd, Gtk, Pango, GLib
from xtreme_shell.modules.utils import get_paintable_from_path, to_button, box


class Notification(Gtk.ListBoxRow):
    def __init__(self, notif: AstalNotifd.Notification, removeFunc):
        super().__init__(width_request=300)
        self.notif = notif
        self.remove_func = removeFunc

        timeout = 5000 if (e := notif.get_expire_timeout()) <= 0 else e
        GLib.timeout_add(
            timeout,
            lambda: self.remove_func(self.notif.get_id(), "expired"),
        )

        self.setup_widgets()

    def action_callback(self, button):
        self.notif.invoke(button.id)

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

        left = box(False, children=[icon, title], spacing=5)

        end = Gtk.Image(
            icon_name="window-close-symbolic", opacity=0.6, css_classes=["false-button"]
        )

        to_button(end, lambda _: self.remove_func(self.notif.get_id(), "dismissed"))

        header.set_start_widget(left)
        header.set_end_widget(end)

        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        root.append(sep)

        notification_image = Gtk.Image(pixel_size=64)
        if (paintable := get_paintable_from_path(self.notif.get_image())) is not None:
            notification_image.set_from_paintable(paintable)
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

        if len(self.notif.props.actions) > 0:
            actions = box(
                False,
                children=[self.build_button(x) for x in self.notif.props.actions],
                homogeneous=True,
                spacing=5,
            )
            revealer = Gtk.Revealer(
                transition_type=Gtk.RevealerTransitionType.SLIDE_DOWN,
                transition_duration=200,
                child=actions,
            )

            motion = Gtk.EventControllerMotion.new()
            motion.connect("enter", lambda *_: revealer.set_reveal_child(True))
            motion.connect("leave", lambda *_: revealer.set_reveal_child(False))

            self.add_controller(motion)

            root.append(revealer)
