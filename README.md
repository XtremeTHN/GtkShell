# GtkShell
A gtk shell for my dots

## Installation
Via meson:
```bash
meson setup build
meson install -C build
```

Install the project in pip only if you want autocompletions<br>
Via pip (execute this in the root directory of the repo):
```bash
pip install .
```

## Configuration
Create a file named `config.json` in `~/.config/shell`.
Add `"$schema": "https://raw.githubusercontent.com/XtremeTHN/GtkShell/refs/heads/main/doc/schema.json"` if you want intellisense.

## Styles
Link or copy the `styles` folder to `~/.config/shell/styles`.

## Window names
Here's the window names and namespaces of the shell

| Window name         | Layer namespace     |
|---------------------|---------------------|
| notification-center | astal-notif-center  |
| applauncher         | astal-apps          |
| quicksettings       | astal-quicksettings |
| topbar              | astal-topbar        |
| notifications       | astal-notifications |

## TODO
Maybe i'll add more things to this list
- Greeter
- GcrPrompter for gnome keyring
- To-do list
- ~~Notifications~~
- ~~Add card, bordered and box-10 to box in quicksliders~~
- Fix all devices active in QuickBluetoothMenu
- ~~Weather to bar or quicksettings~~
- Shell and hyprland config manager
- ~~Notification center~~
