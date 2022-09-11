import pyproj
import numpy
import staremaster.sidecar

sinu_wkt = '''  PROJCRS["MODIS Sinusoidal",
                    BASEGEOGCRS["",
                        DATUM["unnamed", ELLIPSOID["WGS 84",6371007.181,0,LENGTHUNIT["metre",1]]],
                        PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433]]],
                CONVERSION["",
                    METHOD["Sinusoidal"],
                    PARAMETER["semi_major",6371007.181],
                    PARAMETER["semi_minor",6371007.181]],
                CS[Cartesian,2],
                    AXIS["(E)",east,ORDER[1],LENGTHUNIT["m",1]],
                    AXIS["(N)",north,ORDER[2],LENGTHUNIT["m",1]]]'''

sinu_crs = pyproj.crs.CRS(sinu_wkt)
r = 6371007.181


def lonlat2xy(lon, lat):
    y = lat * r * (numpy.pi/180)
    x = lon * r * (numpy.cos(numpy.deg2rad(lat))) * (numpy.pi/180)
    return x, y


def xy2lonlat(x, y):
    lat = y / r / (numpy.pi/180)
    lon = x / r / (numpy.cos(numpy.deg2rad(lat))) / (numpy.pi/180)
    return lon, lat


class ModisTile:
    size = 2400  # A tile has 2400x2400 pixels
    res = 463.3127165693852  # (left-right)/2400
    nom_res = '500m'

    def __init__(self, tile_name):
        self.tile_name = tile_name
        self.parse_tile_name()
        self.make_bounds()
        self.make_xy()
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

        #self.left, self.top = lonlat2xy(west, north)
        #self.right, self.bottom = lonlat2xy(east, south)
        _, self.top = lonlat2xy(0, north)
        _, self.bottom = lonlat2xy(0, south)
        self.left, _ = lonlat2xy(west, 0)
        self.right, _ = lonlat2xy(east, 0)

    def make_xy(self):
        self.xs = numpy.tile(numpy.arange(self.left, self.right, self.res), (self.size, 1)) + self.res / 2
        self.ys = numpy.tile(numpy.arange(self.top, self.bottom, -self.res), (self.size, 1)).T + self.res / 2

    def make_latlon(self):
        lons, lats = xy2lonlat(self.xs, self.ys)
        self.lats = numpy.ascontiguousarray(lats)
        self.lons = numpy.ascontiguousarray(lons)

    def make_cover_sids(self, n_workers=1):
        self.cover_sids = staremaster.conversions.merge_stare(self.sids, dissolve_sids=False, n_workers=n_workers, n_chunks=1)

    def make_sids(self, n_workers):
        self.sids = staremaster.conversions.latlon2stare(self.lats, self.lons, resolution=None,
                                                         n_workers=n_workers, adapt_resolution=True)

    def create_sidecar(self, out_path, n_workers=1):
        self.make_sids(n_workers=n_workers)
        self.make_cover_sids(n_workers=n_workers)

        i = self.lats.shape[0]
        j = self.lats.shape[1]
        l = self.cover_sids.size

        sidecar = staremaster.sidecar.Sidecar(granule_path='{}.hdf'.format(self.tile_name), out_path=out_path)
        sidecar.write_dimensions(i, j, l, nom_res=self.nom_res)
        sidecar.write_sids(self.sids, nom_res=self.nom_res)
        sidecar.write_lons(self.lons, nom_res=self.nom_res)
        sidecar.write_lats(self.lats, nom_res=self.nom_res)
        sidecar.write_cover(self.cover_sids, nom_res=self.nom_res)



