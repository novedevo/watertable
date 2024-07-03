let
  nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-24.05";

  pkgs = import nixpkgs { config = {}; overlays = []; };
in
pkgs.mkShell {
  packages = [
    (pkgs.python3.withPackages (python-pkgs: [
      python-pkgs.numpy
      python-pkgs.requests
      python-pkgs.matplotlib
      python-pkgs.pandas
      python-pkgs.ipykernel
      python-pkgs.pip
      python-pkgs.jupyter
    ]))
    pkgs.jupyter-all
    pkgs.ruff
  ];
}