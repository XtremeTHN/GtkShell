import logging
from xtreme_shell.modules.style import compile_scss_string
from gi.repository import Gtk


class Widget(Gtk.Widget):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def set_css(self, css):
        ctx = getattr(self, "ctx", None) or self.get_style_context()

        if (n := getattr(self, "_provider", None)) is not None:
            ctx.remove_provider(n)

        provider = Gtk.CssProvider.new()
        provider.load_from_string(css)

        ctx.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        setattr(self, "_provider", provider)
