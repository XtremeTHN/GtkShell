from gi.repository import AstalNetwork, Gdk, GLib
from requests import get

from xtreme_shell.lib.config import (
    Config,
    WeatherLocationTypes,
    WeatherProviders,
    WeatherUnits,
)
from xtreme_shell.lib.logger import getLogger
from xtreme_shell.lib.network import NWrapper
from xtreme_shell.lib.task import Task
from xtreme_shell.lib.utils import Object, get_signal_args


def download(url, cb):
    def __down():
        try:
            cb(get(url))
        except Exception as e:
            getLogger("download").error(
                f"Couldn't fetch information from '{url}' because {[str(x) for x in e.args]}"
            )

    Task(__down).start()


def get_public_ip():
    try:
        return get("https://api.ipify.org").text
    except Exception as e:
        getLogger("get_public_ip").error(
            f"Couldn't fetch public ip because {' '.join(e.args)}"
        )


class FreeWeather(Object):
    __gsignals__ = {"changed": get_signal_args("run_last")}

    def __init__(self):
        super().__init__()
        self.logger = getLogger("FreeWeather")

        self.nm = NWrapper.get_default()
        self.conf = Config().get_default().weather
        self.url = "http://api.weatherapi.com/v1/current.json?key={}&q={}&aqi=no"
        self.temp = 0
        self.condition = ""
        self.paintable = None

        self.__location_id = self.conf.location.on_change(self.update)
        self.__unit_id = self.conf.unit.on_change(self.update)
        self.__api_key = self.conf.api_key.on_change(self.update)
        self.__round_temp_id = self.conf.round_temp.on_change(self.update)

        self.update()

    def disconnect_all(self):
        self.conf.location.disconnect(self.__location_id)
        self.conf.unit.disconnect(self.__unit_id)
        self.conf.api_key.disconnect(self.__api_key)
        self.conf.round_temp.disconnect(self.__round_temp_id)

    def __on_updated(self, cnt):
        cnt: dict = cnt.json()
        if (e := cnt.get("error")) is not None:
            self.logger.warning("Error while fetching weather data: %s", e["message"])
            return

        if self.conf.unit.value == WeatherUnits.CENTIGRADE:
            self.temp = cnt["current"]["temp_c"]
        elif self.conf.unit.value == WeatherUnits.FAHRENHEIT:
            self.temp = cnt["current"]["temp_f"]

        if self.conf.round_temp.value:
            self.temp = round(self.temp)

        self.condition = cnt["current"]["condition"]["text"]
        download(
            "https:" + cnt["current"]["condition"]["icon"],
            self.__on_icon_loaded,
        )
        self.emit("changed")

    def update(self, *_):
        if self.nm.net.get_state() == AstalNetwork.State.CONNECTED_GLOBAL:
            location = self.conf.location.value
            if self.conf.location_type.value == WeatherLocationTypes.IP:
                location = get_public_ip()

            download(
                self.url.format(self.conf.api_key.value, location),
                self.__on_updated,
            )

    def __on_icon_loaded(self, contents):
        self.paintable = Gdk.Texture.new_from_bytes(GLib.Bytes.new(contents.content))
        self.emit("changed")


class Weather(Object):
    def __init__(self):
        super().__init__()

        self.conf = Config().get_default().weather
        self.manager = None

        self.conf.provider.on_change(self.__on_provider_changed, once=True)

    def __on_provider_changed(self, _):
        if self.manager is not None:
            self.manager.disconnect_all()
        if self.conf.provider.value == WeatherProviders.FREEWEATHER:
            self.manager = FreeWeather()
        self.manager.update()
