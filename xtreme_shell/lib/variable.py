from gi.repository import GObject


class Variable(GObject.GObject):
    __gsignals__ = {"changed": (GObject.SIGNAL_RUN_FIRST, None, tuple())}

    def __init__(self, value):
        GObject.GObject.__init__(self)
        self.__value = value

    def connect_notify(self, func, *user_data):
        self.connect("notify::value", lambda *_: func(*user_data))

    @GObject.Property()
    def value(self):
        return self.get_value()

    @value.setter
    def value(self, val):
        self.set_value()

    def set_value(self, val):
        self.__value = val
        self.notify("value")
        self.emit("changed")

    def get_value(self):
        return self.__value
