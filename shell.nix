# Reference: <https://nixos.wiki/wiki/Python>
{pkgs ? import <nixpkgs> {}}: let
  deps = ps:
    with ps; [
      setuptools

      # For formatting
      black

      # Deps
      pytz
      requests
      nextcord
    ];
  python = pkgs.python3.withPackages deps; # Python3.11 as of writing
in
  python.env
