'''
GUI for computing the range and relative azimuth between the ARMOR and MAX
radars from user-entered lat/lon coordinates.

Azimuths are geodetic bearings (WGS84), measured clockwise from true north.
"Azimuth of MAX relative to ARMOR" is the bearing you'd point along from
ARMOR to look at MAX, and vice versa.
'''

import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, ttk

import pyproj

GEOD = pyproj.Geod(ellps='WGS84')

# ARMOR is a fixed site, so its coordinates are pre-filled. MAX is a mobile
# radar, so its coordinates are pre-filled with its default parking spot in
# the UAH SWIRLL lot but can be overwritten for each deployment.
DEFAULT_ARMOR_LAT = 34.646156
DEFAULT_ARMOR_LON = -86.771458
DEFAULT_MAX_LAT = 34.72475082014219
DEFAULT_MAX_LON = -86.64705155757972

BASE_FONT_SIZE = 10
MIN_SCALE = 0.7
MAX_SCALE = 3.0


def compute_geometry(armor_lat, armor_lon, max_lat, max_lon):
    """Return (az_max_from_armor, az_armor_from_max, range_km), all geodetic."""
    az_to_max, az_to_armor, dist_m = GEOD.inv(armor_lon, armor_lat, max_lon, max_lat)
    return az_to_max % 360, az_to_armor % 360, dist_m / 1000


class RelativeGeometryApp:
    def __init__(self, root):
        self.root = root
        root.title('ARMOR / MAX Relative Geometry')

        # All text and entry sizing routes through these two shared font
        # objects, so rescaling them rescales every widget that uses them.
        self.normal_font = tkfont.Font(family='TkDefaultFont', size=BASE_FONT_SIZE)
        self.bold_font = tkfont.Font(
            family='TkDefaultFont', size=BASE_FONT_SIZE, weight='bold')
        self._scale = 1.0
        self._resize_job = None

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        frame = ttk.Frame(root, padding=12)
        frame.grid(row=0, column=0, sticky='nsew')
        frame.columnconfigure(1, weight=1)
        # Every row shares the weight equally so any slack between the
        # window's actual size and the content's natural size is spread
        # thinly across the whole layout, instead of collecting as one
        # empty block below the last row.
        for row in range(8):
            frame.rowconfigure(row, weight=1)

        self.armor_lat = tk.StringVar(value=str(DEFAULT_ARMOR_LAT))
        self.armor_lon = tk.StringVar(value=str(DEFAULT_ARMOR_LON))
        self.max_lat = tk.StringVar(value=str(DEFAULT_MAX_LAT))
        self.max_lon = tk.StringVar(value=str(DEFAULT_MAX_LON))

        ttk.Label(frame, text='ARMOR', font=self.bold_font).grid(
            row=0, column=0, columnspan=2, sticky='w')
        self._add_coord_row(frame, 1, 'Latitude', self.armor_lat)
        self._add_coord_row(frame, 2, 'Longitude', self.armor_lon)

        ttk.Label(frame, text='MAX', font=self.bold_font).grid(
            row=3, column=0, columnspan=2, sticky='w', pady=(10, 0))
        self._add_coord_row(frame, 4, 'Latitude', self.max_lat)
        self._add_coord_row(frame, 5, 'Longitude', self.max_lon)

        ttk.Button(
            frame, text='Compute', command=self.on_compute,
        ).grid(row=6, column=0, columnspan=2, pady=10)

        self.result_var = tk.StringVar(value='')
        self.result_label = ttk.Label(
            frame, textvariable=self.result_var, justify='left', anchor='nw',
            font=self.normal_font)
        self.result_label.grid(row=7, column=0, columnspan=2, sticky='nsew', pady=(10, 0))
        self.result_label.bind(
            '<Configure>', lambda e: self.result_label.configure(wraplength=e.width))

        # Size the window to the content's actual natural size (no reserved
        # blank space), and use that size as the scaling baseline so a
        # scale of 1.0 always corresponds to "just fits the content." Measure
        # with a 3-line placeholder in the result area first so the baseline
        # already has room for a real result once Compute is clicked.
        self.result_var.set('placeholder\nplaceholder\nplaceholder')
        root.update_idletasks()
        self.base_width = frame.winfo_reqwidth()
        self.base_height = frame.winfo_reqheight()
        self.result_var.set('')
        root.geometry(f'{self.base_width}x{self.base_height}')
        root.minsize(round(self.base_width * MIN_SCALE), round(self.base_height * MIN_SCALE))

        root.bind('<Configure>', self._on_root_configure)

    def _add_coord_row(self, frame, row, label, var):
        ttk.Label(frame, text=label, font=self.normal_font).grid(
            row=row, column=0, sticky='w', padx=(0, 8))
        ttk.Entry(frame, textvariable=var, width=15, font=self.normal_font).grid(
            row=row, column=1, sticky='ew')

    def _on_root_configure(self, event):
        if event.widget is not self.root:
            return
        if self._resize_job is not None:
            self.root.after_cancel(self._resize_job)
        self._resize_job = self.root.after(80, self._apply_scale, event.width, event.height)

    def _apply_scale(self, width, height):
        self._resize_job = None
        scale = min(width / self.base_width, height / self.base_height)
        scale = max(MIN_SCALE, min(scale, MAX_SCALE))
        if abs(scale - self._scale) < 0.03:
            return
        self._scale = scale
        size = max(6, round(BASE_FONT_SIZE * scale))
        self.normal_font.configure(size=size)
        self.bold_font.configure(size=size)

    def on_compute(self):
        try:
            armor_lat = float(self.armor_lat.get())
            armor_lon = float(self.armor_lon.get())
            max_lat = float(self.max_lat.get())
            max_lon = float(self.max_lon.get())
        except ValueError:
            messagebox.showerror('Invalid input', 'All coordinates must be numeric.')
            return

        az_max_from_armor, az_armor_from_max, range_km = compute_geometry(
            armor_lat, armor_lon, max_lat, max_lon)

        self.result_var.set(
            f'Range: {range_km:.3f} km\n'
            f'Azimuth of MAX relative to ARMOR: {az_max_from_armor:.2f}\N{DEGREE SIGN}\n'
            f'Azimuth of ARMOR relative to MAX: {az_armor_from_max:.2f}\N{DEGREE SIGN}'
        )


if __name__ == '__main__':
    root = tk.Tk()
    app = RelativeGeometryApp(root)
    root.mainloop()
