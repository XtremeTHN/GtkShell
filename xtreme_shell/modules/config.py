from .services.opt import Json, opt

_conf = Json.get_default()

class Option:
    def __init__(self, _type: type, default=None):
        self.key = ""
        self._type = _type
        self.default = default
    
    def __set_name__(self, owner, key: str):
        self.key = key.replace("_", "-")
    
    def __get__(self, obj, objtype=None):
        return _conf.get_opt(self.key, self._type, default=self.default)

class BarConfig:
    date_format = Option(str, default="%I:%M %p %b %Y")
    fallback_title = Option(str, default="NixOS")
