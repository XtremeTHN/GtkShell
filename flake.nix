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
      requests
      inotify
      pygobject3
      pypdf
    ]));

    nativeBuildInputs = with pkgs; [
      meson
      ninja
      wrapGAppsHook
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

      python
      pkgs.poppler_gi
      pkgs.coreutils
      pkgs.dart-sass  
      pkgs.gobject-introspection
      pkgs.networkmanager
      pkgs.gtk4
      pkgs.gtk4-layer-shell
      pkgs.libadwaita
    ];

  in {
    devShells.${system}.default = pkgs.mkShell {
      venvDir = ".venv";
      PYTHONPATH = ''${python}/${python.sitePackages}:$PYTHONPATH'';
      packages = nativeBuildInputs ++ buildInputs ++ [
        python.pkgs.venvShellHook
        pkgs.pkg-config
      ];
    };
    packages.${system}.default = pkgs.python311Packages.buildPythonApplication rec {
      version = "0.1.0";
      pname = "xtreme_shell";
      name = "${pname}-${version}";
      pyproject = false;
      src = ./.;
      
      inherit nativeBuildInputs buildInputs;

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
        makeWrapperArgs+=(--prefix PYTHONPATH : "${self}/${python.sitePackages}:$PYTHONPATH")
        makeWrapperArgs+=("''${gappsWrapperArgs[@]}")
      '';
    };
  };
}
