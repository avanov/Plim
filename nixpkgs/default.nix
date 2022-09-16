let

common-src = builtins.fetchTarball {
    name = "common-2022-09-15";
    url = https://github.com/avanov/nix-common/archive/6e47c05632c781e0279f4b4609fb4125e4e7bf67.tar.gz;
    # Hash obtained using `nix-prefetch-url --unpack <url>`
    sha256 = "sha256:1av8r2wn4nqwldkkmij4pig9x4nhii7x053i0bd1ngi66kxdkxhr";
};

in

import common-src { projectOverlays = []; }
