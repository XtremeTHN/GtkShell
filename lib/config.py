from lib.constants import JSON_CONFIG_PATH
from lib.services.opt import Json
from lib.utils import Object


class DefaultWindowConfig:

    def __init__(self, conf, _class):
        self.enabled = conf.get_opt(f"{_class}.enabled", default=True)
        self.show_on_start = conf.get_opt(f"{_class}.show-on-start",
                                          default=False)


class BarConfig():

    def __init__(self, conf):
        self.enabled = conf.get_opt("bar.enabled")
        self.fallback_window_name = conf.get_opt("bar.fallback-name",
                                                 default="ArchLinux")
        self.music_player = conf.get_opt("bar.music-player", default="spotify")


class QuickSettingsConfig(DefaultWindowConfig):

    def __init__(self, conf):
        super().__init__(conf, "quicksettings")
        self.profile_picture = conf.get_opt("quicksettings.profile-picture")
        self.quick_username = conf.get_opt("quicksettings.quick-username")

        self.quick_blue_enabled = conf.get_opt(
            "quicksettings.bluetooth.enabled")
        self.quick_blue_show_no_name = conf.get_opt(
            "quicksettings.bluetooth.show-no-name", default=False)


class Config(Object):

    def __init__(self):
        self.conf = Json(JSON_CONFIG_PATH)
        self.bar = BarConfig(self.conf)
        self.apprunner = AppRunnerConfig(self.conf)
        self.quicksettings = QuickSettingsConfig(self.conf)

        self.wallpaper = self.conf.get_opt("background.wallpaper")
