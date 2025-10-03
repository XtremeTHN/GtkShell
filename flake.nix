{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    astal = {
      url = "github:aylur/astal";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, astal }: let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
    python = (pkgs.python3.withPackages (ps: with ps; [
      pygobject3
      rich
    ]));

    nativeBuildInputs = with pkgs; [
      meson
      ninja
      wrapGAppsHook
      blueprint-compiler
    ];

    buildInputs = with astal.packages.${system}; [
      io
      astal4
      battery
      hyprland
      wireplumber
      mpris
      tray
      bluetooth
      apps
      notifd
      network
      cava

      python
      pkgs.dart-sass
      pkgs.gobject-introspection
      pkgs.gtk4
      pkgs.gtk4-layer-shell
      pkgs.libadwaita
    ];

  in {
    devShells.${system}.default = pkgs.mkShell {
      inherit nativeBuildInputs buildInputs;

      packages =  [
        pkgs.pkg-config
      ];
    };
    packages.${system}.default = pkgs.stdenv.mkDerivation {
      name = "shell";
      version = "0.1.0";
      src = ./.;
      
      inherit nativeBuildInputs buildInputs;

      postPatch = ''
        substituteInPlace xtreme_shell/modules/versions.py \
            --replace "libgtk4-layer-shell.so" "${pkgs.gtk4-layer-shell}/lib/libgtk4-layer-shell.so"
      '';
    };
  };
}