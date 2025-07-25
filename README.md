# GtkShell
A gtk shell for my dots. This project is not finished, expect crashes.

## Installation
You need the following packages (archlinux packages names):
- `python`
- `python-pygobject`
- `python-requests`
- `gtk4-layer-shell`
- `astal-meta`
- `python-inotify`

### Meson:
```bash
meson setup build
meson install -C build
```
### Pip
Install the project in pip only if you want autocompletions<br>
Execute this in the root directory of the repo:
```bash
pip install .
```
### NixOS
Add this repository to your flake inputs
```nix
# flake.nix
inputs.xtremeShell = {
  url = "github:XtremeTHN/GtkShell;
  inputs.nixpkgs.follows = "nixpkgs";
};
```
Then add xtremeShell to the `home.packages` or `environment.systemPackages`.
```nix
# home.nix
home.packages = [
  inputs.xtremeShell.packages."x86_64-linux".default
];
```

## Configuration
Create a file named `config.json` in `~/.config/shell`. And add this:
```json 
{
  "$schema": "https://raw.githubusercontent.com/XtremeTHN/GtkShell/refs/heads/main/doc/schema.json"
}
```

## Window names

| Window name         | Layer namespace     |
|---------------------|---------------------|
| notification-center | astal-notif-center  |
| applauncher         | astal-apps          |
| quicksettings       | astal-quicksettings |
| topbar              | astal-topbar        |
| notifications       | astal-notifications |

## TODO
Maybe i'll add more things to this list
- [ ] Greeter
- [x] GcrPrompter for gnome keyring unlocking ([GPrompt](https://github.com/XtremeTHN/GPrompt))
- [ ] To-do list
- [x] Notifications
- [x] Add card, bordered and box 10 to box in quicksliders
- [ ] Fix all devices active in QuickBluetoothMenu
- [x] Weather in bar or quicksettings
- [ ] Shell and hyprland config manager
- [x] Notification center
- [ ] Fix wifi connect prompt
- [ ] Add wifi qr support
- [ ] Create an utility for sharing data between devices
- [ ] Fix double free when setting weather icon (issue #1)
- [x] Implement external modules
- [x] Add a module that joins pdfs ([ShellPlugins](https://github.com/XtremeTHN/ShellPlugins))
- [x] Add blur to music art with GtkSnapshot.push_blur()
- [ ] *Rewrite*