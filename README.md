# GtkShell
A gtk shell for my dots

## Installation
##### NixOS
Add this repository to inputs in your nix flake
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

##### Meson:
```bash
meson setup build
meson install -C build
```
##### Pip
Install the project in pip only if you want autocompletions<br>
Execute this in the root directory of the repo:
```bash
pip install .
```

## Configuration
Create a file named `config.json` in `~/.config/shell`. And add this:
```json 
{
  "$schema": "https://raw.githubusercontent.com/XtremeTHN/GtkShell/refs/heads/main/doc/schema.json"
}
```

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
