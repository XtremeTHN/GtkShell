from gi.repository import Gdk
import logging


def get_paintable_from_path(path) -> Gdk.Paintable | None:
    if path is None:
        return None
    try:
        txt = Gdk.Texture.new_from_filename(path)
        return txt
    except Exception:
        logging.getLogger("get_paintable_from_path").exception(
            f"Can't get paintable. Path: {path}"
        )
        return None
