from gi.repository import AstalPowerProfiles, GObject, Gtk
from .button import ButtonService, QuickButton


class PowerMan(ButtonService):
    def __init__(self, button: QuickButton):
        super().__init__(button, connectClicked=False)

        self.power = AstalPowerProfiles.get_default()
        self.power.bind_property(
            "icon-name", button.icon, "icon-name", GObject.BindingFlags.SYNC_CREATE
        )

        self.power.connect("notify::active-profile", self.on_profile_change)
        self.widget.subtitle.set_visible(True)

        self.on_profile_change()

    def on_profile_change(self, *_):
        profile = self.power.get_active_profile()

        self.active = profile != "balanced"

        self.widget.subtitle.set_label(profile.replace("-", " ").title())
