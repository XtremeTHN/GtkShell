from xtreme_shell.modules.utils import Blp, notify
from xtreme_shell.modules.services.loginone import LoginOne

from gi.repository import Gtk, Gio, Astal, GLib

from .menu import QuickMenu
from .button import QuickButton
from .network import NetManager
from .bluetooth import BluetoothManager
from .power import PowerMan

import logging


@Blp("quick-settings")
class QuickSettings(Astal.Window):
    __gtype_name__ = "QuickSettings"

    power_btt: Gtk.Button = Gtk.Template.Child()
    power_menu: QuickMenu = Gtk.Template.Child()

    audio_scale: Gtk.Scale = Gtk.Template.Child()
    brightness_scale: Gtk.Scale = Gtk.Template.Child()

    network_btt: QuickButton = Gtk.Template.Child()
    bluetooth_btt: QuickButton = Gtk.Template.Child()

    connections_menu: QuickMenu = Gtk.Template.Child()

    power_mode_btt: QuickButton = Gtk.Template.Child()
    night_light_btt: QuickButton = Gtk.Template.Child()

    profile_menu: QuickMenu = Gtk.Template.Child()

    def __init__(self):
        super().__init__(
            name="quick-settings",
            namespace="shell-quick-ssettings",
            layer=Astal.Layer.OVERLAY,
            resizable=False,
        )

        self.login = LoginOne.get_default()
        self.logger = logging.getLogger("QuickSettings")

        BluetoothManager(self.bluetooth_btt)
        NetManager(self.network_btt)
        PowerMan(self.power_mode_btt)

        self.power_btt.connect("clicked", self.power_menu.toggle)

        self.add_css_class("quicksettings")
        self.present()
        # self.set_visible(False)

    @Gtk.Template.Callback()
    def screenshot(self, _):
        def finish(obj: Gio.Subprocess, res):
            try:
                obj.wait_check_finish(res)
            except GLib.Error:
                notify(
                    self,
                    "Screenshot",
                    f"Couldn't take screenshot: {obj.get_exit_status()}",
                )

        # TODO: Make a screenshoter
        proc = Gio.Subprocess.new(
            ["hyprshot", "-m", "region"], Gio.SubprocessFlags.NONE
        )
        proc.wait_check_async(None, finish)

    @Gtk.Template.Callback()
    def settings(self, _):
        self.logger.info("Not implemented")

    @Gtk.Template.Callback()
    def lock(self, _):
        self.logger.info("Not implemented")

    @Gtk.Template.Callback()
    def suspend(self, _):
        if self.login.can_suspend():
            self.login.suspend()
            return

        notify(self, "QuickSettings", "Can't suspend now")
        return
