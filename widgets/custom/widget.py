from gi.repository import Gtk

from lib.logger import getLogger
from lib.style import Style


class CustomizableWidget:
    def __init__(self, **kwargs):
        self.__provider = None
        self.__bg_id = 0
        self.logger = getLogger(self.__class__.__name__)
        pass

    def set_background_opt(self, opt):
        if self.background_opacity is not None and self.__bg_id != 0:
            self.background_opacity.disconnect(self.__bg_id)

        self.background_opacity = opt
        self.__bg_id = self.background_opacity.on_change(self.change_opacity)
        self.change_opacity(None)

    def set_css(self, css_string: str):
        try:
            css = Style.compile_scss_string(css_string)
        except RuntimeError:
            self.logger.exception("Failed to compile scss section")
            return

        ctx = self.get_style_context()
        if self.__provider is not None:
            ctx.remove_provider(self.__provider)

        self.__provider = Gtk.CssProvider.new()
        self.__provider.load_from_string(css)

        ctx.add_provider(self.__provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def change_opacity(self, _):
        self.set_css(
            f"background-color: rgba(colors.$background, {self.background_opacity.value});"
        )
        self.logger.debug("Changed opacity to %s", self.background_opacity.value)
