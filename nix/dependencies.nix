{pkgs, ...}: rec {
  nativeBuildInputs = with pkgs; [
  ];

  buildInputs = with pkgs; [
  ];

  all = nativeBuildInputs ++ buildInputs;
}
