from lib.constants import JSON_CONFIG_PATH
from lib.services.opt import Json
from lib.utils import Object


class Config(Object):

    def __init__(self):
        self.conf = Json(JSON_CONFIG_PATH)

        self.wallpaper = self.conf.get_opt("background.wallpaper")

        self.fallback_window_name = self.conf.get_opt(
            "bar.active-window.fallback-name", default="ArchLinux")
        self.player = self.conf.get_opt("bar.music-player", default="spotify")

        self.profile_picture = self.conf.get_opt(
            "quicksettings.profile-picture")
        self.quick_username = self.conf.get_opt("quicksettings.username")

        self.quick_blue_show_no_name = self.conf.get_opt(
            "quicksettings.bluetooth.show-no-name", default=True)
