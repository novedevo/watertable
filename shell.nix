let
  nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-23.11";

  pkgs = import nixpkgs { config = {}; overlays = []; };
in
pkgs.mkShell {
  packages = [
    (pkgs.python3.withPackages (python-pkgs: [
      python-pkgs.numpy
      python-pkgs.requests
      python-pkgs.matplotlib
    ]))
  ];
}