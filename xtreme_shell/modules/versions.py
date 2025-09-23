from ctypes import CDLL


def init_libraries():
    CDLL("libgtk4-layer-shell.so")
    import gi

    gi.require_versions(
        {"Gtk4LayerShell": "1.0", "Astal": "4.0", "Gtk": "4.0", "Adw": "1"}
    )

    gi.require_versions(
        {
            "AstalIO": "0.1",
            "AstalHyprland": "0.1",
            "AstalNetwork": "0.1"
        }
    )
