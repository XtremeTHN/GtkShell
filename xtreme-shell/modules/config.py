from .services.opt import Json, opt
from typing import TypeVar

from .constants import CONFIG_DIR


class BaseConf:
    def __init__(self, conf, namespace):
        self.conf = conf
        self.namespace = namespace

    def get_opt(self, key: str, _type: type, default) -> opt:
        return self.conf.get_opt(self.namespace + key, _type, default)


class BarConfig(BaseConf):
    def __init__(self, json: Json):
        super().__init__(json, "bar")
        self.date_format = self.get_opt("date-format", str, "%I:%M %p %b %Y")


T = TypeVar("T", bound="Config")


class Config:
    _instance: T = None

    def __init__(self):
        json = Json(CONFIG_DIR / "config.json")
        self.bar = BarConfig(json)

    @classmethod
    def get_default(cls):
        if cls._instance is not None:
            return cls._instance
        cls._instance = Config()
        return cls._instance
