import numpy
import staremaster.sidecar

r = 6371007.181


def lonlat2xy(lon, lat):
    y = lat * r * (numpy.pi/180)
    x = lon * r * (numpy.cos(numpy.deg2rad(lat))) * (numpy.pi/180)
    return x, y


def xy2lonlat(x, y):
    lat = y / r / (numpy.pi/180)
    lon = x / r / (numpy.cos(numpy.deg2rad(lat))) / (numpy.pi/180)
    return lon, lat


class ModisTile():
    size = 2400  # A tile has 2400x2400 pixels
    res = 463.3127165693852  # (left-right)/2400
    nom_res = '500m'

    def __init__(self, tile_name):
        self.tile_name = tile_name

        self.h = None
        self.v = None
        self.parse_tile_name()

        self.tile_top = None
        self.tile_bottom = None
        self.tile_left = None
        self.tile_right = None
        self.make_bounds()

        self.x_cells_sinu = None
        self.y_cells_sinu = None
        self.make_xy()

        self.cells_lats = None
        self.cells_lons = None
        self.make_latlon()

    def parse_tile_name(self):
        h, v = self.tile_name[1:].split('v')
        self.h = int(h)
        self.v = int(v)

    def make_bounds(self):
        west = -180 + self.h * 10
        east = west+10
        north = 90 - self.v * 10
        south = north-10

        _, self.tile_top = lonlat2xy(0, north)
        _, self.tile_bottom = lonlat2xy(0, south)
        self.tile_left, _ = lonlat2xy(west, 0)
        self.tile_right, _ = lonlat2xy(east, 0)

    def make_xy(self):
        self.x_cells_sinu = numpy.tile(numpy.arange(self.tile_left, self.tile_right, self.res), (self.size, 1)) + self.res / 2
        self.y_cells_sinu = numpy.tile(numpy.arange(self.tile_top, self.tile_bottom, -self.res), (self.size, 1)).T - self.res / 2

    def make_latlon(self):
        lons, lats = xy2lonlat(self.x_cells_sinu, self.y_cells_sinu)
        self.cells_lats = numpy.ascontiguousarray(lats)
        self.cells_lons = numpy.ascontiguousarray(lons)

    def make_cover_sids(self, n_workers=1):
        self.cover_sids = staremaster.conversions.merge_stare(self.sids, dissolve_sids=False,
                                                              n_workers=n_workers, n_chunks=1)

    def make_sids(self, n_workers):
        self.sids = staremaster.conversions.latlon2stare(self.cells_lats, self.cells_lons, resolution=None,
                                                         n_workers=n_workers, adapt_resolution=True)

    def create_sidecar(self, out_path, n_workers=1):
        self.make_sids(n_workers=n_workers)
        self.make_cover_sids(n_workers=n_workers)

        i = self.cells_lats.shape[0]
        j = self.cells_lats.shape[1]
        l = self.cover_sids.size

        sidecar = staremaster.sidecar.Sidecar(granule_path='{}.hdf'.format(self.tile_name), out_path=out_path)
        sidecar.write_dimensions(i, j, l, nom_res=self.nom_res)
        sidecar.write_sids(self.sids, nom_res=self.nom_res)
        sidecar.write_lons(self.cells_lons, nom_res=self.nom_res)
        sidecar.write_lats(self.cells_lats, nom_res=self.nom_res)
        sidecar.write_cover(self.cover_sids, nom_res=self.nom_res)



