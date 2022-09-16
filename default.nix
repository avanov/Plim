# https://nixos.wiki/wiki/Development_environment_with_nix-shell
{   pkgs            ? (import ./nixpkgs).pkgs
,   pyVersion       ? "310"
}:

let

python = pkgs."python${pyVersion}Full";
pythonPkgs = pkgs."python${pyVersion}Packages";

devEnv = pkgs.mkShellNoCC {
     name = "plim-devenv";

     # The packages in the `buildInputs` list will be added to the PATH in our shell
     # Python-specific guide:
     # https://github.com/NixOS/nixpkgs/blob/master/doc/languages-frameworks/python.section.md
     nativeBuildInputs = with pkgs; [
         # see https://nixos.org/nixos/packages.html
         # Python distribution
         python
         pythonPkgs.virtualenv
         pythonPkgs.wheel
         pythonPkgs.twine
         pythonPkgs.coveralls

         gnumake
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
         export LANG=en_GB.UTF-8

         # https://python-poetry.org/docs/configuration/
         export PIP_CACHE_DIR="$PWD/.local/pip-cache${pyVersion}"

         # Setup virtualenv
         if [ ! -d $VENV_DIR ]; then
             virtualenv $PWD/.venv
             $VENV_DIR/bin/python -m pip install -e $PWD
             $VENV_DIR/bin/python -m pip install -r $PWD/requirements.txt
         fi

         if [ ! -d $PWD/node_modules ]; then
             npm install stylus
         fi
     '';
};

in
{
    inherit devEnv;
}
