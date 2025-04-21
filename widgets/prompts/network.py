from gi.repository import Gtk, Adw, Astal, GObject
from gi.repository.AstalNetwork import AccessPoint

from widgets.custom.box import Box
from lib.network import NWrapper
from lib.logger import getLogger


class Background(Astal.Window):
    def __init__(self):
        super().__init__(
            namespace="astal-background",
            css_classes=["background"],
            anchor=Astal.WindowAnchor.TOP
            | Astal.WindowAnchor.RIGHT
            | Astal.WindowAnchor.BOTTOM
            | Astal.WindowAnchor.LEFT,
            layer=Astal.Layer.TOP,
            opacity=0.4,
        )


class Spinner(Box):
    def __init__(self, size=14, description=None):
        super().__init__(vertical=True, spacing=10)
        self.desc = Gtk.Label.new(description)
        self.spinner = Adw.Spinner.new()
        self.spinner.props.width_request = size
        self.spinner.props.height_request = size
        self.append_all([self.desc, self.spinner])


class PasswordPage(Box):
    __gsignals__ = {
        "next-page": (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        "cancel": (GObject.SIGNAL_RUN_FIRST, None, tuple()),
    }

    def __init__(self, ap: AccessPoint):
        super().__init__(vertical=True, spacing=10)

        desc = Gtk.Label.new("Provide a password for %s" % ap.get_ssid())

        entry_box = Box(vertical=True, spacing=1)

        self.error_msg = Gtk.Label(xalign=0)
        self.revealer = Gtk.Revealer(
            child=self.error_msg,
            transition_duration=400,
            transition_type=Gtk.RevealerTransitionType.SLIDE_UP,
        )

        self.password = Gtk.PasswordEntry(show_peek_icon=True)
        self.password.connect("activate", self.__next_page)

        entry_box.append_all([self.revealer, self.password])

        cancel_btt = Gtk.Button(label="Cancel", valign=Gtk.Align.CENTER)
        cancel_btt.connect("clicked", self.__send_close)

        self.append_all([desc, entry_box, cancel_btt])

    def reveal_error(self, msg):
        self.error_msg.set_label(msg)
        self.revealer.set_reveal_child(True)

    def __send_close(self, _):
        self.emit("cancel")

    def __next_page(self, _):
        self.emit("next-page", self.password.get_text())


class NetworkPromptNavigator(Gtk.Stack):
    def __init__(self, access_point: AccessPoint):
        super().__init__(transition_type=Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.ap = access_point
        self.logger = getLogger("NetPromptNav")
        self.net = NWrapper.get_default()

        self._pass = PasswordPage(access_point)
        self._pass.connect("next-page", self.__on_next_page)

        loading = Spinner(
            size=24, description="Connecting to %s" % access_point.get_ssid()
        )

        self.add_named(self._pass, "password")
        self.add_named(loading, "loading")

    def __on_error(self, msg):
        self.set_visible_child_name("password")
        self._pass.reveal_error(msg)

    def __on_connection_finish(self, client, res):
        try:
            client.add_and_activate_connection_finish(res)
            self._pass.emit("cancel")
        except Exception as e:
            self.logger.exception("Error")
            self.__on_error(" ".join(e.args))

    def __on_next_page(self, _, password):
        self.set_visible_child_name("loading")
        self.net.connect_to_ssid(self.ap, password, self.__on_connection_finish)


class NetworkPrompt(Astal.Window):
    def __init__(self, access_point: AccessPoint):
        super().__init__(
            exclusivity=Astal.Exclusivity.NORMAL,
            keymode=Astal.Keymode.ON_DEMAND,
            css_classes=["network-prompt", "background"],
        )

        self.background = Background()
        self.background.present()

        content = Box(vertical=True, spacing=20, valign=Gtk.Align.CENTER)

        title = Gtk.Label(label="Network", css_classes=["title-1"])
        nav = NetworkPromptNavigator(access_point)
        nav._pass.connect("cancel", lambda _: self.close())

        content.append_all([title, nav])

        self.set_child(content)
        self.present()

    def close(self):
        super().close()
        self.background.close()
