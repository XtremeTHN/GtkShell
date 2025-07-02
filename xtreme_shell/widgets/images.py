from gi.repository import Gtk, GObject


class BlurryImage(Gtk.Picture):
    def __init__(self, blur: int | float = 0, **kwargs):
        super().__init__(**kwargs)
        self.__blur = blur

    @GObject.Property
    def blur(self):
        return self.__blur

    @blur.setter
    def blur(self, blur):
        self.__blur = blur
        self.notify("blur")

    def do_snapshot(self, snapshot):
        snapshot.push_blur(self.blur)
        Gtk.Picture.do_snapshot(self, snapshot)
        snapshot.pop()
