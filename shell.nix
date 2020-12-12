with (import (builtins.fetchTarball {
  # Descriptive name to make the store path easier to identify
  name = "typeit-python39";
  # Commit hash for nixos-unstable as of 2019-10-27
  url = https://github.com/NixOS/nixpkgs/archive/2c0f6135aab77ff942b615228882c7dd996e0882.tar.gz;
  # Hash obtained using `nix-prefetch-url --unpack <url>`
  sha256 = "00yg8dck4ymcifrxsknnpms52n16xnb8yiqjkby002mbm2aflf45";
}) {});

# Make a new "derivation" that represents our shell
stdenv.mkDerivation {
    name = "plim39";

    # The packages in the `buildInputs` list will be added to the PATH in our shell
    # Python-specific guide:
    # https://github.com/NixOS/nixpkgs/blob/master/doc/languages-frameworks/python.section.md
    buildInputs = [
        # see https://nixos.org/nixos/packages.html
        # Python distribution
        python39Full
        python39Packages.virtualenv
        python39Packages.wheel
        python39Packages.twine
        nodejs
        nodePackages.npm
        taglib
        ncurses
        libxml2
        libxslt
        libzip
        zlib
        # root CA certificates
        cacert
        which
    ];
    shellHook = ''
        # set SOURCE_DATE_EPOCH so that we can use python wheels
        export SOURCE_DATE_EPOCH=$(date +%s)
        VENV_DIR=$PWD/.venv
        export PATH=$VENV_DIR/bin:$PATH
        export PYTHONPATH=""
        export LANG=en_US.UTF-8
        # https://python-poetry.org/docs/configuration/
        export PIP_CACHE_DIR=$PWD/.local/pip-cache
        # Setup virtualenv
        if [ ! -d $VENV_DIR ]; then
            virtualenv $PWD/.venv
        fi
    '';
}
