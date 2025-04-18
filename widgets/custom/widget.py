from gi.repository import Astal, Gtk
from lib.logger import getLogger
from lib.style import Style

class CustomizableWidget:
    def __init__(self, **kwargs):
        self.__provider = None
        self.logger = getLogger(self.__class__.__name__)
        pass

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
        self.set_css(f'background-color: rgba(colors.$background, {self.background_opacity.value});')
        self.logger.debug("Changed opacity to %s", self.background_opacity.value)