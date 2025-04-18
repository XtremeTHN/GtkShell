from gi.repository import Gtk, Astal, Gdk, GLib, Adw
from lib.logger import getLogger
from lib.config import Config

from widgets.quick.scales import BacklightSlider, AudioSlider
from widgets.quick.buttons.bluetooth import QuickBluetooth
from widgets.quick.buttons.network import QuickNetwork
from widgets.custom.widget import CustomizableWidget
from widgets.quick.buttons.tray import QuickSysTray
from widgets.quick.buttons.audio import QuickMixer
from widgets.custom.box import Box


def get_pretty_seconds(seconds):
    dias = int(seconds // 86400)
    horas = int((seconds % 86400) // 3600)
    minutos = int((seconds % 3600) // 60)
    return dias, horas, minutos


class Uptime(Gtk.Label):

    def __init__(self):
        super().__init__(css_classes=["uptime"], xalign=0)
        self.proc_uptime = open("/proc/uptime", 'r')
        self.logger = getLogger("Uptime")
        self.update()

    def update(self, *_, **__):
        cnt = self.proc_uptime.read().split(" ")
        self.proc_uptime.seek(0)
        time = get_pretty_seconds(float(cnt[0]))

        string = "up "
        if time[0] != 0:
            string += f"{time[0]} days,"
        elif time[1] != 0:
            string += f"{time[1]} hours,"
        elif time[2] != 0:
            string += f"{time[2]} minutes"

        if time[0] == 0 and time[1] == 0 and time[2] == 0:
            string += "less than a minute"
        self.set_label(string.strip(","))


class MainPage(Box):

    def __init__(self, stack):
        super().__init__(vertical=True, spacing=10)

        self.config: Config = Config.get_default()
        self.logger = getLogger(self.__class__.__name__)
        self.stack: Gtk.Stack = stack

        # Top part of the window
        self.top = Box(spacing=10)
        self.label_box = Box(vertical=True,
                             spacing=0,
                             css_classes=["quick-labels"])

        self.pfp = Adw.Avatar(size=48)
        self.name = Gtk.Label(css_classes=["quick-name"], xalign=0)
        self.uptime = Uptime()

        self.label_box.append_all([self.name, self.uptime])
        self.top.append_all([self.pfp, self.label_box])

        # Center box
        self.center = Box(spacing=10, homogeneous=True, vertical=True)
        self.center.append_all(
            [QuickNetwork(),
             QuickBluetooth(),
             QuickSysTray(),
             QuickMixer()],
            map_func=lambda w: w.set_stack(self.stack))

        # End box
        self.end = Box(spacing=10, vertical=True, margin_top=5)
        self.end.append_all([BacklightSlider(), AudioSlider()])

        # Connections
        self.config.quicksettings.quick_username.on_change(self._update_name,
                                                           once=True)
        self.config.quicksettings.profile_picture.on_change(self.__update_pfp,
                                                            once=True)

        self.append_all([self.top, self.center, self.end])

    def _update_name(self, *_):
        usr = self.config.quicksettings.quick_username
        if usr.is_set() is False:
            environ = GLib.get_environ()
            user = [
                var.split("=")[1] for var in environ if var.startswith("USER")
            ]
            self.name.set_text(user[0].title())
        else:
            self.name.set_text(usr.value)

    def _update_uptime(self, *_):
        self.uptime.update()

    def __update_pfp(self, _):
        pfp = self.config.quicksettings.profile_picture
        self.logger.debug("Changing profile picture...")
        self.logger.debug("Path: %s", pfp.value)
        if pfp.is_set():
            try:
                img = Gdk.Texture.new_from_filename(pfp.value)
                self.pfp.set_custom_image(img)
            except:
                self.logger.exception("Couldn't apply texture to Gtk.Picture")
                return
        else:
            self.pfp.set_icon_name("avatar-default-symbolic")


class QuickSettingsContent(Gtk.Stack, CustomizableWidget):

    def __init__(self):
        Gtk.Stack.__init__(self,
            css_classes=["quicksettings-content"],
            transition_type=Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        CustomizableWidget.__init__(self)
        self.config = Config.get_default()
        self.background_opacity = self.config.quicksettings.background_opacity

        self.main_page = MainPage(self)

        self.background_opacity.on_change(self.change_opacity, once=True)
        self.add_named(self.main_page, "main")
        self.set_visible_child_name("main")

class QuickSettings(Astal.Window):

    def __init__(self):
        # Set resizable to false. When the quick menu shows, the window will go back to its original size
        super().__init__(namespace="astal-quicksettings",
                         name="quicksettings",
                         anchor=Astal.WindowAnchor.TOP
                         | Astal.WindowAnchor.RIGHT,
                         exclusivity=Astal.Exclusivity.NORMAL,
                         css_classes=["quicksettings-window"],
                         resizable=False)
        _conf = Config.get_default()
        self.content = QuickSettingsContent()
        self.set_child(self.content)

        self.connect("notify::visible", self.content.main_page._update_uptime)

        self.set_margin_top(10)
        self.set_margin_right(10)

        self.present()
        self.set_visible(_conf.quicksettings.show_on_start.value)

    @staticmethod
    def is_enabled():
        return Config.get_default().quicksettings.enabled.value
