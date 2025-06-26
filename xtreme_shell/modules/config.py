from .services.opt import Json, opt
import logging

_conf = Json.get_default()


# it's a bit ugly
class Option:
    """
    A descriptor for getting configs from Json service.

    This class allows defining class-level attributes that retrieves an option from the Json service.
    The key is based on the class name and the attribute name, with underscores replaced by hyphens.

    Parameters:
        _type (type): The expected type of the configuration value.
        default (Any, optional): The default value to return if the key is not defined.
    """

    logger = logging.getLogger("Option")

    def __init__(self, _type: type, default=None):
        if not isinstance(default, _type):
            raise TypeError(
                f'Expected "{_type.__name__}" from default keyword, got {type(default).__name__}'
            )
        self.key = ""
        self._type = _type
        self.default = default

    def __set_name__(self, owner, key: str):
        def replace(string):
            return string.replace("_", "-")

        parent_keys = owner.__name__.lower().split("_")
        self.key = ".".join([".".join(parent_keys), replace(key)])

    def __get__(self, obj, objtype=None):
        return _conf.get_opt(self.key, self._type, default=self.default)


class Bar:
    date_format = Option(str, default="%I:%M %p %b %Y")
    fallback_title = Option(str, default="NixOS")
    opacity = Option(float, default=1.0)
    enabled = Option(bool, default=True)


class Corners:
    opacity = Option(float, default=1.0)
    enabled_corners = Option(list, default=[])
    enabled = Option(bool, default=True)
