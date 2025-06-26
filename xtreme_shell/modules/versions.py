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
            "AstalCava": "0.1",
            "AstalHyprland": "0.1",
            "AstalNetwork": "0.1",
            "AstalWp": "0.1",
            "AstalBattery": "0.1",
            "AstalMpris": "0.1",
            "AstalTray": "0.1",
            "AstalBluetooth": "0.1",
            "AstalApps": "0.1",
            "AstalNotifd": "0.1",
        }
    )
