import logging
from xtreme_shell.modules.services.opt import opt
from xtreme_shell.modules.style import compile_scss_string
from gi.repository import Gtk


class Widget(Gtk.Widget):
    logger = logging.getLogger("Widget")

    @classmethod
    def set_css(cls, widget, css, no_heading=False, no_curly_braces=False):
        if css == "":
            raise ValueError("Provide some css pls")
        try:
            compiled_css = compile_scss_string(
                css,
                no_heading=no_heading,
                no_curly_braces=no_curly_braces,
                ignoreErrors=True,
            )
        except Exception:
            cls.logger.exception("Error while trying to compile css string")
            return
        else:
            ctx = getattr(widget, "ctx", None) or widget.get_style_context()

            if (n := getattr(widget, "_provider", None)) is not None:
                ctx.remove_provider(n)

            provider = Gtk.CssProvider.new()
            provider.load_from_string(compiled_css)

            ctx.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
            setattr(widget, "_provider", provider)

    @classmethod
    def __change_opacity(cls, widget, opacity):
        cls.set_css(widget, f"background-color: rgba(colors.$background, {opacity});")

    @classmethod
    def set_opacity_option(cls, widget, option: opt):
        option.on_change(lambda o: cls.__change_opacity(widget, o), once=True)
