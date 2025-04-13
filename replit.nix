{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.flask
    pkgs.python311Packages.pillow
    pkgs.imagemagick_light
  ];
}
