#! /usr/bin/env python -tt
# -*- coding: utf-8; mode: python -*-
r"""Sidecar creation utility for NASA's MERRA-2 Reanalysis (also MCMS)

merra2.py
~~~~~~~~~

Edit: STAREMaster_py/staremaster/products/__init__.py
    Add:
        from staremaster.products.merra2 import MERRA2

Edit: STAREMaster_py/staremaster/create_sidecar_file.py
    Add:
        def create_grid_sidecar():
            elif grid == 'merra2':
                granule = staremaster.products.MERRA2(for_mcms)
                granule.load()
        def create_sidecar():
            elif product == 'MERRA2':
                granule = staremaster.products.MERRA2(file_path)
        def guess_product():
            elif 'MERRA2' in file_path and '.nc4' in file_name:
                product = 'MERRA2'
        def main():
            parser.add_argument('--as_mcms', metavar='as_mcms', type=int,
                                help='MCMS specific layout for MERRA2 grid', default=0)

Create sidecar file:

    $ cd /Users/mbauer/SpatioTemporal/STAREMaster_py/staremaster

    $ python create_sidecar_files.py --workers 1 --product merra2 --grid MERRA2 --out_path /Users/mbauer/tmp/output/merra2_files/
or
    $ python create_sidecar_files.py --workers 1 --product merra2 --grid MERRA2 --out_path /Users/mbauer/tmp/output/merra2_files/ --as_mcms 1


$ cd ~/.ssh; ssh-add bayesics_mbauer_id_rsa mbauer288-GitHub_id_ed25519 id_ed25519; cd; source bash_profile_CONDA.sh; conda activate stare; cd /Users/mbauer/SpatioTemporal/STAREMaster_py/staremaster

See

"""
# Standard Imports
import os
import pickle

# Third-Party Imports
# import netCDF4
import numpy as np

# STARE Imports
from staremaster.sidecar import Sidecar
import staremaster.conversions
import pystare

##
# List of Public objects from this module.
__all__ = ['MERRA2']

##
# Markup Language Specification (see Google Python Style Guide https://google.github.io/styleguide/pyguide.html)
__docformat__ = "Google en"
# ------------------------------------------------------------------------------

###############################################################################
# PUBLIC Class: MERRA2
# --------------------
class MERRA2:
    """Specification for the data-grid of the NASA MERRA-2 Reanalysis (ASM, 3 hourly).

    ======================================================================
    MERRA-2 NATIVE RESOLUTION
        0.5 x 0.625 centered on (-180, -90)

        * The horizontal discretization of the MERRA-2 model output is placed on a latitude-longitude grid.
            * The sea-level pressure field used by MCMS represents instantaneous point measurements at the mid-points of this latitude-longitude grid.
            * That is, the data is Point-Registered:
                * The data grids represent a 2D set of unconnected coordinate pairs, which may or may not be regularly spaced, with no areal extent (i.e., no cells).
            * It is also sometimes referred to as an Uniform/Equi-Angular latitude grid.
                * The poles are at corners/edges of first and last grid-cells.
                * The dateline is at west edge of first longitude grid-cell.
            * From the MERRA-2 documentation we get.
                The horizontal native grid origin, associated with variables indexed (i=0, j=0) represents a grid-point located at (180W, 90S).
                Latitude and longitude of grid-points as a function of their indices (i, j) or (col, row) and can be determined by:

                    nlon = 576
                    nlat = 361
                    dlon = 0.625 deg
                    dlat = 0.5 deg

                    lon_i = -180.0 + dlon * i, where i = 0, nlon - 1
                    lat_j =  -90.0 + dlat * j, where j = 0, nlat - 1

                For example,
                    (i = 0       , j =        0) corresponds to a grid point at (lon =     -180, lat = -90)
                    (i = nlon - 1, j =        0) corresponds to a grid point at (lon = +179.375, lat = -90)
                    ...
                    (i = 288     , j =      180) corresponds to a grid point at (lon =       0,  lat =   0)
                    ...
                    (i = 0       , j = nlat - 1) corresponds to a grid point at (lon =     -180, lat = +90)
                    (i = nlon - 1, j = nlat - 1) corresponds to a grid point at (lon = +179.375, lat = +90)

                Giving a domain range of grid-points:

                    (+179.375, +90)|(-180, +90) ... (+179.375, +90)|(+180, +90)
                                   |.           ...               .|
                                   |.           ...               .|
                    (+179.375, -90)|(-180, -90) ... (+179.375, -90)|(+180, -90)

                    * The cyclic nature of longitude works here in terms of thinking of these as regularly dlon spaced points.
                        +179.375 + dlon = +180
                        -180 - dlon = -180.625 == +179.375

                        Indeed, we can see how these can be taken as grid-cells centered on the mid-points with edges offset by half dlon (0.3125 deg).
                                                                                                                         Wrap Around<>Wrap Around
                            |(+179.6875)-------(-180.0000)-------(-179.6875)|  ...  |(+179.0625)-------(+179.3750)-------(+179.6875)||(+179.6875)-------(-180.0000)-------(-179.6875)
                                                  i = 0                        ...                     i = nlon - 1                                        i = 0
                    * The polar singularities in latitude are fine in the sense the first and last rows are at the poles, which means
                      each col has the same value in these rows (i.e., the poles are a single point).

                      It is more difficult to portray the latitude grid as a series of grid-cells centered on the mid-points with edges offset by half dlat (0.025 deg).

                            Here lat_m are the latitude mid-points and lat_e are the latitude edges.
                                ------------------- -90.25 = lat_e[0]
                                lat_m[0]   = -90.00
                                ------------------- -89.75 = lat_e[1]
                                lat_m[1]   = -89.50
                                ------------------- -89.25 = lat_e[2]
                                ...
                                ------------------- +89.25 = lat_e[359]
                                lat_m[359] = +89.50
                                ------------------- +89.75 = lat_e[360]
                                lat_m[360] = +90.00
                                ------------------- +90.25 = lat_e[361]

                        The issue here is that the polar grids extend past the poles or are half-grid in height.
                            * One way to handle this is to consider the polar row as being half-height triangles rather than rectangular (i.e., ignore the past-pole extent).
                                * Basically, in the polar-most rows the x-edges and x-centers are the same (given the polar point contains all longitudes).

                                    Half-Height Triangular Cell:
                                                                ------------------[-180.0, +90.0]-----------------
                                                                |                                                |
                                            [+179.6875, +89.75] -------------------------------------------------- [-179.6875, +89.75]
                                                                |                                                |
                                                                |                 [-180.0, +89.5]                |
                                                                |                                                |
                                             [+179.6875, +75.0] -------------------------------------------------- [-179.6875, +75.0]
                                                                .                                                .
                                                                .                                                .
                                                                .                                                .
                                             [+179.6875, -75.0] -------------------------------------------------- [-179.6875, -75.0]
                                                                |                                                |
                                                                |                 [-180.0, -89.5]                |
                                                                |                                                |
                                            [+179.6875, -89.75] -------------------------------------------------- [-179.6875, -89.75]
                                                                |                                                |
                                                                ------------------[-180.0, -90.0]-----------------
                            * Other software either ignore the polar overshoot, or don't treat the data-points as a data-grid, to avoid this problem.
                    * Thus, the MERRA-2 is a sort of regular, but asymmetrical data-grid.
                        * The coordinates are regular, but their implied boundaries are irregular (at the poles in this case).

        MCMS and MERRA-2
            * For MCMS, MERRA-2 is one of the many data-grids it must deal with. As a result, MCMS reorganizes each input dataset to a common framework.
                1) For most among these is that MCMS works with data-grids rather than data-points.
                    * That is, MCMS treats the MERRA-2 data-points is being a Grid- or Gridline-Registered data-grid.
                        * The given coordinates represent the mid-points of the data-cells.
                        * The edges/gridlines are one-half the grid height and width to the left and down from the mid-points.
                            (grid_edge_x[col], grid_edge_y[row + 1])---------------------------------------(grid_edge_x[col + 1], grid_edge_y[row + 1])
                                                                    |                                      |
                                                                    |            grid[col, row]            |
                                                                    |                                      |
                            (grid_edge_x[col],     grid_edge_y[row])---------------------------------------(grid_edge_x[col + 1],     grid_edge_y[row])
                    * The first and last columns and rows of data-grids thus straddle the edges of the grid domain.
                2) For some operations, such as storage, it is easier for MCMS to have longitudes as positive values (i.e., 0-360 rather than +/-180).
                    * For MERRA-2 then lon_m[0] = -180.0 is converted to 180.0
                3) Do to point 2), MCMS shifts the origin of the data-grid so that its first column/longitude is near zero degrees.
                    * For MERRA-2 then lon_m[0] = 180.0 is shifted so that to lon_m_360[0] = 0.0, lon_m_260[288] = 180.0 and lon_m_260[575] = 359.375
    ======================================================================
    """

    ###########################################################################
    # PRIVATE Instance-Constructor: __init__()
    # ----------------------------------------
    def __init__(self, as_mcms):
        """Initialize MERRA2"""
        ##
        # Declare Public-Attributes

        # String path to where sidecar file is to be stored
        # self.file_path = file_path

        # Array of grid/point mid-point/center latitudes (units: deg, format: +/-90)
        self.lats = []

        # Array of grid/point mid-point/center longitudes (units: deg, format: +/-180)
        self.lons = []

        # Array of STARE Spatial Indices (SIDs)
        self.sids = []

        # Array of STARE cover SIDs
        self.cover_sids = []

        # String identifier for data-grids with different resolutions (N/A to MERRA-2)
        self.nom_res = ''

        # Flag to use the MCMS specific layout
        self.as_mcms = as_mcms


    ###########################################################################
    # PUBLIC Instance-Method: load()
    # ------------------------------
    def load(self):
        self.get_latlon()

    ###########################################################################
    # PUBLIC Instance-Method: get_latlon()
    # ------------------------------------
    def get_latlon(self):
        """Data Grid defined by the NASA MERRA-2 Reanalysis."""
        # print("\tget_latlon():")

        # Number of columns/longitudes of the data-grid.
        nlon = 576

        # Number of rows/latitudes of the data-grid.
        nlat = 361

        # Number of enumerated data-points in the data-grid (nlon * nlat).
        maxid = 207936

        # Column holding the middle data-grid longitude.
        halfway = 288

        # Row holding the equator latitude
        eq_grid = 180

        # Grid Spacing X/Lon degrees (5/8 degrees)
        dx = 0.625
        dx_half = 0.3125

        # Grid Spacing Y/Lat degrees (1/2 degrees)
        dy = 0.5
        dy_half = 0.25

        # Set starting point
        first_lat_mpnt = -90.0
        first_lon_mpnt = 0.0 if self.as_mcms else -180.0

        # Mid-point latitudes of data-grid (-90 to +90)
        r"""
        get_latlon(as_mcms = False):
            lats (361, 576):
                Min: -90.0000
                Max: +90.0000
                [ -90.0,  -89.5 ...   +89.5,  +90.0]
                [(0, 0), (1, 0) ... (-2, 0), (-1, 0)]
            lons (361, 576):
                Min: -180.000
                Max: +179.375
                [-180.000, -179.375 ... +178.750, +179.375]
                [(0, 0),   (0, 1)   ... (0, -2),  (0, -1)]

        get_latlon(as_mcms = 1):
            lats (361, 576):
                Min: -90.0
                Max: +90.0
                [-90.0, -89.5 ... +89.5, +90.0]
                [(0, 0), (1, 0) ... (-2, 0), (-1, 0)]
            lons (361, 576):
                Min: +0.000
                Max: +359.375
                [+0.000, +0.625 ... +358.750, +359.375]
                [(0, 0), (0, 1) ... (0, -2), (0, -1)]
        """
        self.lats = np.ascontiguousarray(np.tile(np.linspace(first_lat_mpnt, -1.0 * first_lat_mpnt, num=nlat, endpoint=True), (nlon, 1)).transpose())

        # Mid-point longitudes of data-grid (-180 to +179.375)
        if self.as_mcms:
            self.lons = np.tile(np.linspace(first_lon_mpnt, 359.375, num=nlon, endpoint=True), (nlat, 1))
        else:
            self.lons = np.tile(np.linspace(first_lon_mpnt, 179.375, num=nlon, endpoint=True), (nlat, 1))
        # print(f"\nget_latlon(as_mcms = {self.as_mcms}):")
        # print(f"\tlats {self.lats.shape}:")
        # print(f"\t\tMin: {np.amin(self.lats):+.1f}")
        # print(f"\t\tMax: {np.amax(self.lats):+.1f}")
        # print(f"\t\t[{self.lats[0, 0]:+.1f}, {self.lats[1, 0]:+.1f} ... {self.lats[-2, 0]:+.1f}, {self.lats[-1, 0]:+.1f}]")
        # print("\t\t[(0, 0), (1, 0) ... (-2, 0), (-1, 0)]")
        # print(f"\tlons {self.lons.shape}:")
        # print(f"\t\tMin: {np.amin(self.lons):+.3f}")
        # print(f"\t\tMax: {np.amax(self.lons):+.3f}")
        # print(f"\t\t[{self.lons[0, 0]:+.3f}, {self.lons[0, 1]:+.3f} ... {self.lons[0, -2]:+.3f}, {self.lons[0, -1]:+.3f}]")
        # print("\t\t[(0, 0), (0, 1) ... (0, -2), (0, -1)]")

    ###########################################################################
    # PUBLIC Instance-Method: make_sids()
    # -----------------------------------
    def make_sids(self):
        """
        def from_latlon_2d(lat, lon, level=None, adapt_level=False, fill_value_in=None, fill_value_out=None):
            Coverts latitudes and longitudes to SIDs. The STARE Level can be automatically adapted match the resolution of the geolocations.

            level: int (0<=level<=27)
                Level of the SIDs.
                    If unset, level will me automatically adapted.
                    If set, adapt_level will be set to false.
            adapt_level: bool
                if True, level will adapted to match resolution of lat/lon.
                Overwrites level.
            fill_value_in: STARE indices are not calculated for lat/lon of this value
            fill_value_out: set indices to this value where lat/lon is fill_value_in

        Gives same result as staremaster.conversions.latlon2stare()
        """
        # Note:
        #   in pystare -> if adapt_level: level = 27
        # self.sids = pystare.from_latlon_2d(self.lats, self.lons, adapt_level=True)
        self.sids = pystare.from_latlon_2d(self.lats, self.lons, level=10, adapt_level=False)
        r"""
        make_sids(as_mcms = 1):
            self.sids.shape = (361, 576)
                type(self.sids) = <class 'numpy.ndarray'> type(self.sids[0, 0]) = <class 'numpy.int64'>
                self.sids[0, 0] = 2287822013634445311
                sids_res = 7

        make_sids(as_mcms = 0):
            self.sids.shape = (361, 576)
                type(self.sids) = <class 'numpy.ndarray'> type(self.sids[0, 0]) = <class 'numpy.int64'>
                self.sids[0, 0] = 2287822013634445311
                sids_res = 7

            STARE Q-Level to form indices.
            | Q-Level | R        | L          |
            |---------|---------:|-----------:|
            | 27      |          | ~0.1m      |
            | ...     |          |            |
            | 23      |~1 m      | ~1.2 m     |
            | 22      |~2 m      | ~2.4 m     |
            | 21      |~4 m      | ~5 m       |
            | 20      |~8 m      | ~10 m      |
            | 19      |~15 m     | ~19 m      |
            | 18      |~31 m     | ~38 m      |
            | 17      |~61 m     | ~77 m      |
            | 16      |~122 m    | ~153 m     |
            | 15      |~245 m    | ~307 m     |
            | 14      |~490 m    | ~615 m     |
            | 13      |~1 km     | ~1.2 km    |
            | 12      |~2 km     | ~2 km      |
            | 11      | ~4 km    | ~5 km      |
            | 10      | ~8 km    | ~10 km     |
            | 09      | ~16 km   | ~20 km     |
            | 08      | ~31 km   | ~39 km     |
            | 07      | ~63 km   | ~78 km     | <= sids_res
            | 06      | ~125 km  | ~157 km    |
            | 05      | ~251 km  | ~314 km    |
            | 04      | ~501 km  | ~628 km    |
            | 03      | ~1003 km | ~1,256 km  |
            | 02      | ~2005 km | ~2,500 km  |
            | 01      | ~4011 km | ~5,000 km  |
            | 00      | ~8021 km | ~10,000 km |
            [Table 1. Approximate uncertainties in terms of the area
                      (radius (R)) and the edge length (L) of the trixel by Q-level.]
        """
        # print(f"\tmake_sids(as_mcms = {self.as_mcms}):")
        sids_res = staremaster.conversions.min_resolution(self.sids)
        # print(f"{self.sids.shape = }")
        # print(f"{type(self.sids) = } {type(self.sids[0, 0]) = }")
        # print(f"{self.sids[0, 0] = }")
        # print(f"{sids_res = }")

    ###########################################################################
    # PUBLIC Instance-Method: load_sids_pickle()
    # ------------------------------------------
    def load_sids_pickle(self, pickle_name):
        with open(pickle_name, 'rb') as pickel_file:
            self.sids = pickle.load(pickel_file)

    ###########################################################################
    # PUBLIC Instance-Method: save_sids_pickle()
    # ------------------------------------------
    def save_sids_pickle(self, pickle_name):
        with open(pickle_name, 'wb') as pickel_file:
            pickle.dump(self.sids, pickel_file)

    ###########################################################################
    # PUBLIC Instance-Method: load_cover_pickle()
    # ------------------------------------------
    def load_cover_pickle(self, pickle_name):
        with open(pickle_name, 'rb') as pickel_file:
            self.cover_sids = pickle.load(pickel_file)

    ###########################################################################
    # PUBLIC Instance-Method: save_cover_pickle()
    # ------------------------------------------
    def save_cover_pickle(self, pickle_name):
        with open(pickle_name, 'wb') as pickel_file:
            pickle.dump(self.cover_sids, pickel_file)

    ###########################################################################
    # PUBLIC Instance-Method: get_sids()
    # ----------------------------------
    def get_sids(self, out_path):
        # print(f"\tget_sids({out_path = }):")
        if self.as_mcms:
            pickle_name = f"{out_path}merra2_mcms_sids.pkl"
        else:
            pickle_name = f"{out_path}merra2_sids.pkl"
        if os.path.exists(pickle_name):
            ##
            # Read SIDs from file
            self.load_sids_pickle(pickle_name)
        else:
            ##
            # Determine SIDs
            self.make_sids()
            ##
            # Save SIDs to pickle
            self.save_sids_pickle(pickle_name)

    ###########################################################################
    # PUBLIC Instance-Method: get_cover()
    # ----------------------------------
    def get_cover(self, out_path):
        """
        cover_res           = 5

        STARE Q-Level to form indices.
        | Q-Level | R        | L          |
        |---------|---------:|-----------:|
        | 27      |          | ~0.1m      |
        | ...     |          |            |
        | 23      |~1 m      | ~1.2 m     |
        | 22      |~2 m      | ~2.4 m     |
        | 21      |~4 m      | ~5 m       |
        | 20      |~8 m      | ~10 m      |
        | 19      |~15 m     | ~19 m      |
        | 18      |~31 m     | ~38 m      |
        | 17      |~61 m     | ~77 m      |
        | 16      |~122 m    | ~153 m     |
        | 15      |~245 m    | ~307 m     |
        | 14      |~490 m    | ~615 m     |
        | 13      |~1 km     | ~1.2 km    |
        | 12      |~2 km     | ~2 km      |
        | 11      | ~4 km    | ~5 km      |
        | 10      | ~8 km    | ~10 km     |
        | 09      | ~16 km   | ~20 km     |
        | 08      | ~31 km   | ~39 km     |
        | 07      | ~63 km   | ~78 km     | <= sids_res
        | 06      | ~125 km  | ~157 km    |
        | 05      | ~251 km  | ~314 km    | <= cover_res
        | 04      | ~501 km  | ~628 km    |
        | 03      | ~1003 km | ~1,256 km  |
        | 02      | ~2005 km | ~2,500 km  |
        | 01      | ~4011 km | ~5,000 km  |
        | 00      | ~8021 km | ~10,000 km |
        [Table 1. Approximate uncertainties in terms of the area
                  (radius (R)) and the edge length (L) of the trixel by Q-level.]

        sids_adapted.shape  = (361, 576)
        type(sids_adapted)  = <class 'numpy.ndarray'> type(sids_adapted[0, 0]) = <class 'numpy.int64'>
        sids_adapted[0, 0]  = 2287822013634445285
        cf. self.sids[0, 0] = 2287822013634445311

        self.cover_sids.shape = (8,)
        type(self.cover_sids) = <class 'numpy.ndarray'> type(self.cover_sids[0]) = <class 'numpy.int64'>
        self.cover_sids       = [0  576460752303423488 1152921504606846976 1729382256910270464 2305843009213693952 2882303761517117440 3458764513820540928 4035225266123964416]
        """
        # print(f"get_cover({out_path = }):")
        if self.as_mcms:
            pickle_name = f"{out_path}merra2_mcms_cover_sids.pkl"
        else:
            pickle_name = f"{out_path}merra2_cover_sids.pkl"
        if os.path.exists(pickle_name):
            ##
            # Read cover from file
            self.load_cover_pickle(pickle_name)
            return

        ##
        # Find a Q-Level for cover encoding
        cover_res = staremaster.conversions.min_resolution(self.sids)
        # print(f"\t{cover_res = }")

        # Drop the resolution to make the cover less sparse
        cover_res -= 2
        if cover_res < 0:
            cover_res = 0
        # print(f"\t{cover_res = }")

        ##
        # Clear the SID location bits up to the encoded spatial resolution
        sids_adapted = pystare.spatial_coerce_resolution(self.sids, cover_res)
        # print(f"\t{sids_adapted.shape = }")
        # print(f"\t{type(sids_adapted) = } {type(sids_adapted[0, 0]) = }")
        # print(f"\t{sids_adapted[0, 0] = }")
        # print(f"\t{sids_adapted = }")

        ##
        # Find the cover
        self.cover_sids = staremaster.conversions.merge_stare(sids_adapted, n_workers=1)
        # print(f"{self.cover_sids.shape = }")
        # print(f"{type(self.cover_sids) = } {type(self.cover_sids[0]) = }")
        # print(f"{self.cover_sids[0] = }")
        # print(self.cover_sids)

        ##
        # Save cover to pickle
        self.save_cover_pickle(pickle_name)


    ###########################################################################
    # PUBLIC Instance-Method: create_sidecar()
    # ----------------------------------------
    def create_sidecar(self, out_path=None, n_workers=1):
        # print(f"\ncreate_sidecar({out_path = }):")

        ##
        # Find SIDs for each data-point
        self.get_sids(out_path)

        ##
        # Find the STARE cover for self.sids
        self.get_cover(out_path)

        # # Third-Party Imports
        # import matplotlib as mpl
        # import matplotlib.pyplot as plt
        # import matplotlib.tri as tri
        # import cartopy.crs as ccrs
        # import cartopy.feature as cf
        # import shapely
        # from PIL import Image
        # import geopandas

        # ##
        # # Set up the projection and transformation
        # proj = ccrs.PlateCarree()
        # # proj = ccrs.AzimuthalEquidistant(central_longitude=0.0, central_latitude=-90)
        # # proj = ccrs.AzimuthalEquidistant(central_longitude=0.0, central_latitude=90)
        # transf = ccrs.Geodetic()

        # ##
        # # Plot Options
        # plot_options = {'projection':proj, 'transform':transf}
        # default_dpi = mpl.rcParamsDefault['figure.dpi']
        # mpl.rcParams['figure.dpi'] = 1.5 * default_dpi

        # class figax_container(object):
        #     def __init__(self, figax):
        #         self.fig = figax[0]
        #         self.ax  = figax[1]
        #         return

        # def add_coastlines(figax, set_global=False):
        #     "Add coastlines to the plot."
        #     ax = figax.ax
        #     if set_global:
        #         ax.set_global()
        #     ax.coastlines()
        #     return figax

        # def hello_plot(spatial_index_values=None, figax=None, plot_options={'projection':ccrs.PlateCarree(), 'transform':ccrs.Geodetic()}, set_global=False, set_coastlines=True, show=True, color=None, lw=1):
        #     if figax is None:
        #         figax = figax_container(plt.subplots(1, subplot_kw=plot_options))
        #         if set_global:
        #             figax.ax.set_global()
        #         if set_coastlines:
        #             figax.ax.coastlines()
        #     else:
        #         ax = figax.ax

        #     if spatial_index_values is not None:
        #         # Calculate vertices and interconnection matrix
        #         lons, lats, intmat = pystare.triangulate_indices(spatial_index_values)

        #         # Make triangulation object & plot
        #         siv_triang = tri.Triangulation(lons, lats, intmat)
        #         figax.ax.triplot(siv_triang, c=color, transform=plot_options['transform'], lw=lw)

        #     if show:
        #         plt.show()
        #     return figax

        # def plot_segment(i0, i1, figax):
        #     lat = lat0[i0:i1]
        #     lon = lon0[i0:i1]
        #     spatial_id = spatial_id0[i0:i1]
        #     figax = hello_plot(spatial_id, figax=figax, show=False)
        #     figax.ax.scatter([lon], [lat], s=1, c='r')
        #     return figax

        # ##
        # # Plot cover
        # hello_plot(self.cover_sids, plot_options=plot_options, set_global=False, set_coastlines=True)

        ##
        # Make Sidecar
        r"""i = 361, j = 576, l = 8"""
        i = self.lats.shape[0]
        j = self.lats.shape[1]
        l = self.cover_sids.size
        # print(f"{i = }, {j = }, {l = }")

        if self.as_mcms:
            sidecar_name = f"{out_path}merra2_mcms_sidecar.hdf"
        else:
            sidecar_name = f"{out_path}merra2_sidecar.hdf"
        sidecar = Sidecar(granule_path=sidecar_name, out_path=out_path)

        ##
        # Save Sidecar to file
        sidecar.write_dimensions(i, j, l)
        # print(f"{self.sids = }")
        sidecar.write_sids(self.sids, fill_value=0)
        sidecar.write_lons(self.lons)
        sidecar.write_lats(self.lats)
        sidecar.write_cover(self.cover_sids)

# >>>> ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: <<<<
# >>>> END OF FILE | END OF FILE | END OF FILE | END OF FILE | END OF FILE | END OF FILE <<<<
# >>>> ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: <<<<

