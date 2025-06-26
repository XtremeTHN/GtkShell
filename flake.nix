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
    python = (pkgs.python311.withPackages (ps: with ps; [
      pygobject3
      rich
      setproctitle
    ]));

    nativeBuildInputs = with pkgs; [
      meson
      ninja
      wrapGAppsHook
      python
      pkg-config
    ];

    buildInputs = with astal.packages.${system}; [
      io
      cava
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
      pkgs.gtk4
      pkgs.gtk4-layer-shell
      pkgs.libadwaita
    ];

  in {
    devShells.${system}.default = pkgs.mkShell {
      venvDir = ".venv";
      packages = nativeBuildInputs ++ buildInputs ++ [
        python.pkgs.venvShellHook
        pkgs.pkg-config
        pkgs.ruff
      ];
    };
    packages.${system}.default = pkgs.python311Packages.buildPythonApplication rec {
      version = "0.1.0";
      pname = "xtreme-shell";
      name = "${pname}-${version}";
      pyproject = false;
      src = ./.;
      
      inherit nativeBuildInputs buildInputs;

      strictDeps = true;
      doCheck = false;
      dontWrapGApps = true;

      preFixup = ''
        makeWrapperArgs+=(--prefix LD_LIBRARY_PATH : "${pkgs.gtk4-layer-shell}/lib")
        makeWrapperArgs+=(--prefix PATH : "${pkgs.dart-sass}/bin")
        makeWrapperArgs+=(--prefix PYTHONPATH : "${self}/${python.sitePackages}:$PYTHONPATH")
        makeWrapperArgs+=("''${gappsWrapperArgs[@]}")
      '';
    };
  };
}
