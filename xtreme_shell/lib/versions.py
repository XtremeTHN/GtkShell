from ctypes import CDLL

CDLL("libgtk4-layer-shell.so")
import gi


def __require_astal_feats(feature: str | list[str], version="0.1"):
    if isinstance(feature, str):
        feature = [feature]
    for x in feature:
        gi.require_version(f"Astal{x}", version)


def init():
    gi.require_versions({"Astal": "4.0", "Adw": "1", "NM": "1.0"})
    from gi.repository import Adw  # type: ignore

    Adw.init()

    __require_astal_feats(
        [
            "IO",
            "Hyprland",
            "Network",
            "Wp",
            "Battery",
            "Mpris",
            "Tray",
            "Bluetooth",
            "Apps",
            "Notifd",
        ]
    )
