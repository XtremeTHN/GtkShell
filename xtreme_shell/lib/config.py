from .constants import JSON_CONFIG_PATH
from .logger import getLogger
from .services.opt import Json, opt
from .utils import Object


class BaseConfig:
    def __init__(self, conf, _class):
        self.conf = conf
        self._class = _class.strip(".") + "."

    def get_opt(self, key, default=None) -> opt:
        return self.conf.get_opt(self._class + key, default=default)


class DefaultWindowConfig(BaseConfig):
    def __init__(self, conf, _class):
        super().__init__(conf, _class)

        self.enabled = self.get_opt("enabled", default=True)
        self.show_on_start = self.get_opt("show-on-start", default=False)
        self.background_opacity = self.get_opt("background-opacity", default=1)


class MusicConfig(BaseConfig):
    def __init__(self, conf):
        super().__init__(conf, "bar.music")
        self.player = self.get_opt("player", default="spotify")
        self.transparency = self.get_opt("transparency", default=0.8)


class BarConfig(DefaultWindowConfig):
    def __init__(self, conf):
        super().__init__(conf, "bar")
        self.fallback_window_name = self.get_opt("fallback-name", default="ArchLinux")
        self.music = MusicConfig(conf)


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


class WeatherProviders:
    FREEWEATHER = "freeweather"
    OPENWEATHER = "openweather"


class WeatherLocationTypes:
    IP = "ip"
    CITY = "city"
    COORDINATES = "coordinates"


class WeatherUnits:
    CENTIGRADE = "centigrade"
    FAHRENHEIT = "fahrenheit"


class WeatherConfig(BaseConfig):
    def __init__(self, conf):
        super().__init__(conf, "weather")
        self.logger = getLogger("WeatherConfig")

        self.api_key = self.get_opt("api-key")
        self.provider = self.get_opt("provider", default=WeatherProviders.FREEWEATHER)
        self.location_type = self.get_opt(
            "location-type", default=WeatherLocationTypes.IP
        )
        self.location = self.get_opt("location")
        self.unit = self.get_opt("unit", default=WeatherUnits.CENTIGRADE)
        self.round_temp = self.get_opt("round-temp", default=True)

        self.provider.on_change(self.__on_provider_changed, once=True)
        self.location_type.on_change(self.__on_location_type_changed, once=True)
        self.unit.on_change(self.__on_unit_changed, once=True)

    def __on_unit_changed(self, _):
        if self.unit.value not in WeatherUnits.__dict__.values():
            self.logger.warning(f"Invalid unit: {self.unit.value}")

    def __on_location_type_changed(self, _):
        if self.location_type.value not in WeatherLocationTypes.__dict__.values():
            self.logger.warning(f"Invalid location type: {self.location_type.value}")

    def __on_provider_changed(self, _):
        if self.provider.value not in WeatherProviders.__dict__.values():
            self.logger.warning(f"Invalid provider: {self.provider.value}")


class LogWatcherConfig(BaseConfig):
    def __init__(self, conf):
        super().__init__(conf, "log.watcher")
        self.show_stop_messages = self.get_opt("show-stop-messages", default=True)
        self.show_json_event_messages = self.get_opt(
            "show-json-event-messages", default=True
        )


class LogConfig(BaseConfig):
    def __init__(self, conf):
        super().__init__(conf, "log")
        self.watcher = LogWatcherConfig(conf)
        self.level = self.get_opt("level", default="info")


class Config(Object):
    def __init__(self):
        self.conf = Json(JSON_CONFIG_PATH)
        self.log = LogConfig(self.conf)

        self.bar = BarConfig(self.conf)
        self.applauncher = AppLauncherConfig(self.conf)
        self.notifications = NotificationsConfig(self.conf)
        self.quicksettings = QuickSettingsConfig(self.conf)
        self.weather = WeatherConfig(self.conf)

        self.modules = self.conf.get_opt("modules", default=[])

        self.wallpaper = self.conf.get_opt("background.wallpaper")
