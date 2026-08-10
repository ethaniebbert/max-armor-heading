# ARMOR / MAX Relative Geometry

A small Tkinter GUI for computing the range and relative geodetic azimuth
(bearing) between the [ARMOR]([https://www.nsstc.uah.edu/swirll/main/platforms/index.php](https://www.nsstc.uah.edu/swirll/main/platforms/armor.php))
and [MAX]([https://www.nsstc.uah.edu/swirll/main/platforms/index.php](https://www.nsstc.uah.edu/swirll/main/platforms/max.php)) radars,
given lat/lon coordinates.

- **ARMOR** is a fixed site, so its coordinates are pre-filled.
- **MAX** is a mobile radar, so its coordinates default to its usual parking
  spot in the UAH SWIRLL lot but can be overwritten for each deployment.
- Azimuths are geodetic bearings on the WGS84 ellipsoid, measured clockwise
  from true north, computed with [pyproj](https://pyproj4.github.io/pyproj/).

## Install

Requires macOS or Linux with a desktop/display (the GUI needs somewhere to
render — a headless server without X11/VNC won't work).

```bash
git clone https://github.com/ethaniebbert/max-armor-heading.git
cd max-armor-heading
./install.sh
```

This installs [pixi](https://pixi.sh) if it isn't already on your system,
builds the project's Python environment (Python, Tk, pyproj), and adds a
`get-armor-heading` command to `~/.local/bin` (added to your `PATH`
automatically if needed).

Open a new terminal after installing, then run:

```bash
get-armor-heading
```

This launches the GUI in the background, so you're free to close the
terminal or keep using it for other commands.

## Manual setup

If you'd rather not use `install.sh`, with [pixi](https://pixi.sh) installed:

```bash
pixi install
pixi run gui
```

## License

[MIT](LICENSE)
