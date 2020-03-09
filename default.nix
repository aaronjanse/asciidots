with import <nixpkgs> {};

let
	py = python36;
	pyPkgs = py.pkgs;
in stdenv.mkDerivation rec {
  name = "env";
  env = buildEnv { name = name; paths = buildInputs; };
  buildInputs = with pyPkgs; [
    py
    virtualenv
    pip
    click
    pytest
  ];
}
