from lib.constants import JSON_CONFIG_PATH
from lib.services.opt import Json, opt
from lib.utils import Object


class DefaultWindowConfig:
    def __init__(self, conf, _class):
        self.conf = conf
        self._class = _class.strip(".") + "."

        self.enabled = self.get_opt("enabled", default=True)
        self.show_on_start = self.get_opt("show-on-start", default=False)
        self.background_opacity = self.get_opt("background-opacity", default=1)

    def get_opt(self, key, default=None) -> opt:
        return self.conf.get_opt(self._class + key, default=default)


class BarConfig(DefaultWindowConfig):
    def __init__(self, conf):
        super().__init__(conf, "bar")
        self.fallback_window_name = self.get_opt("fallback-name", default="ArchLinux")
        self.music_player = self.get_opt("music-player", default="spotify")


class QuickSettingsConfig(DefaultWindowConfig):
    def __init__(self, conf):
        super().__init__(conf, "quicksettings")
        self.profile_picture = self.get_opt("profile-picture")
        self.quick_username = self.get_opt("quick-username")

        self.quick_blue_enabled = self.get_opt("bluetooth.enabled")
        self.quick_blue_show_no_name = self.get_opt(
            "bluetooth.show-no-name", default=False
        )


class NotificationCenterConfig(DefaultWindowConfig):
    def __init__(self, conf):
        super().__init__(conf, "notifications.center")
        self.enabled = self.get_opt("enabled", default=True)


class NotificationsConfig(DefaultWindowConfig):
    def __init__(self, conf):
        super().__init__(conf, "notifications")
        self.default_expire_timeout = self.get_opt(
            "default-expire-timeout", default=6000
        )
        self.center = NotificationCenterConfig(conf)


class AppLauncherConfig(DefaultWindowConfig):
    def __init__(self, conf):
        super().__init__(conf, "applauncher")
        self.search_delay = self.get_opt("search-delay", default=500)


class Config(Object):
    def __init__(self):
        self.conf = Json(JSON_CONFIG_PATH)
        self.bar = BarConfig(self.conf)
        self.applauncher = AppLauncherConfig(self.conf)
        self.notifications = NotificationsConfig(self.conf)
        self.quicksettings = QuickSettingsConfig(self.conf)

        self.wallpaper = self.conf.get_opt("background.wallpaper")
