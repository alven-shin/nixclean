{
  self,
  lib,
  ...
}: {
  perSystem = {
    config,
    self',
    inputs',
    pkgs,
    ...
  }: let
    deps = import ./dependencies.nix {inherit pkgs;};
  in {
    packages.default = self'.packages.nixclean;
    packages.nixclean = pkgs.stdenv.mkDerivation {
      pname = "nixclean";
      version = "0.1.0";
      src = ../.;

      nativeBuildInputs = [
        pkgs.makeWrapper
      ];

      installPhase = ''
        runHook preInstall

        mkdir -p $out/bin $out/share/nixclean
        cp $src/nixclean.py $out/share/nixclean
        makeWrapper ${pkgs.python3}/bin/python3 $out/bin/nixclean \
          --add-flags "$out/share/nixclean/nixclean.py"

        runHook postInstall
      '';
    };
  };
}
