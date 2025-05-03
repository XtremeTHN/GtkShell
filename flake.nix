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
  in {
    packages.${system}.default = pkgs.python311Packages.buildPythonApplication rec {
      version = "0.1.0";
      pname = "xtreme_shell";
      name = "${pname}-${version}";
      pyproject = false;
      src = ./.;

      nativeBuildInputs = with pkgs; [
        meson
        ninja
        wrapGAppsHook
      ];

      propagatedBuildInputs = [
        (pkgs.python3.withPackages (ps: with ps; [
          requests
          inotify
          pygobject3
        ]))
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
        
        pkgs.coreutils
        pkgs.dart-sass  
        pkgs.gobject-introspection
        pkgs.networkmanager
        pkgs.gtk4
        pkgs.gtk4-layer-shell
        pkgs.libadwaita
      ];

      strictDeps = false;
      doCheck = false;
      dontWrapGApps = true;
      mesonFlags = [
        "-Dudevrules=etc/udev/rules.d"
      ];

      patches = [
        (pkgs.replaceVars ./nix/fixUdevRules.patch {
          chgrp = "${pkgs.coreutils}/bin/chgrp";
          chmod = "${pkgs.coreutils}/bin/chmod";
         })
        ./nix/fixPythonModules.patch
      ];

      preFixup = ''
        makeWrapperArgs+=(--prefix LD_LIBRARY_PATH : "${pkgs.gtk4-layer-shell}/lib")
        makeWrapperArgs+=(--prefix PATH : "${pkgs.dart-sass}/bin")
        makeWrapperArgs+=("''${gappsWrapperArgs[@]}")
      '';
    };
  };
}
