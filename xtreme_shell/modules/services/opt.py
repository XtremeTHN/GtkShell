from xtreme_shell.modules.gobject import ReusableObject, get_signal_args
from xtreme_shell.modules.constants import CONFIG_DIR
from gi.repository import GObject, AstalIO
from pathlib import Path
import logging
import json
import os


class opt(GObject.GObject):
    __gsignals__ = {"changed": get_signal_args()}

    def __init__(self, key: str, _type: object, default):
        """
        Args:
            key (str): The key for this option (supports dotted notation for nested keys).
            _type (object): The expected type of the option value.
            default: The default value for this option.
        """
        super().__init__()
        self.logger = logging.getLogger(f"opt({key})")
        self.key = key
        self._type = _type
        self.default = default
        self.strict = default is None

        self.__value = None
        self.is_set = False

    def on_change(self, callback, *args):
        """
        Connect a callback to the 'changed' signal.

        The callback will be called when the option value changes.
        The new value will be passed as the first argument.

        Args:
            callback (callable): The function to call when the value changes.
            *args: Additional arguments to pass to the callback.
        """

        def cb(_):
            callback(self.__value, *args)

        self.connect("changed", cb)

    @GObject.Property()
    def value(self):
        """
        Get the current value of the option.

        Returns:
            The current value.
        """
        return self.__value

    @value.setter
    def value(self, value):
        """
        Set the value of the option, enforcing type and default value.
        If the new value equals the old value, the changed signal will not be emited

        Args:
            value: The new value to set.
        """
        should_emit = value != self.__value
        if value is None:
            if self.default is not None:
                self.__value = self.default
            else:
                self.logger.warning(f"Expected {self._type.__name__}. Received None.")
            return

        if not isinstance(value, self._type):
            self.logger.warning(
                f"Expected {self._type.__name__}. Received {type(value).__name__}: {value}."
            )
            return

        self.__value = value
        if should_emit:
            self.emit("changed")
            self.notify("value")


class Json(ReusableObject):
    __gsignals__ = {"changed": get_signal_args()}

    def __init__(self, path: Path):
        """
        Args:
            path (Path): Path to the JSON config file.
        """
        super().__init__()
        if not isinstance(path, Path):
            raise ValueError("Expected pathlib.Path")
        self.opts: list[opt] = []
        self.logger = logging.getLogger(f"Json({os.path.basename(path)})")

        if path.exists() is False and path.is_file() is False:
            path.write_text("{}")

        self.file = path
        self.monitor = AstalIO.monitor_file(str(path), self.__on_event)

    def read(self) -> dict:
        """
        Read and parse the JSON config file.

        Returns:
            dict: The parsed JSON content.
        """
        return json.loads(self.file.read_text())

    def get_opt(self, key: str, type: object, default=None) -> opt:
        """
        Create and register an opt instance for a given key.

        Args:
            key (str): The dotted key path to the option.
            type (object): The expected type of the option value.
            default: The default value for the option.

        Returns:
            opt: The created opt instance.
        """
        o = opt(key, type, default)
        self.opts.append(o)
        self.__update_value(o)
        return o

    @classmethod
    def get_default(cls):
        if cls._instance is None:
            cls._instance = cls(CONFIG_DIR / "config.json")

        return cls._instance

    def _get_nested_value(self, data, keys):
        """
        Retrieve a nested value from a dictionary using a list of keys.
        """
        value = data
        for key in keys:
            value = value[key]
        return value

    def __update_value(self, opt, content=None):
        """
        Update the value of an opt instance from the JSON content.
        """
        value = None
        content = content or self.read()
        try:
            value = self._get_nested_value(content, opt.key.split("."))
        except KeyError:
            opt.is_set = False
        opt.value = value
        opt.emit("changed")

    # FIXME: use Task if this blocks too much
    def __on_event(self, *_) -> None:
        """
        Callback for file change events. Updates all registered opts.
        """
        content = self.read()
        for x in self.opts:
            self.__update_value(x, content)
