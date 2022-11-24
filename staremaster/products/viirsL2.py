import netCDF4
import numpy
from staremaster.sidecar import Sidecar
import staremaster.conversions
import glob


class L2VIIRS:

    def __init__(self, file_path):
        self.file_path = file_path
        self.netcdf = netCDF4.Dataset(file_path, 'r', format='NETCDF4')
        self.lats = None
        self.lons = None
        self.gring_lats = None
        self.gring_lons = None

    def load(self):
        self.read_gring()
        self.read_latlon()

    def read_latlon(self):
        self.lats = self.netcdf.groups['geolocation_data']['latitude'][:].data.astype(numpy.double)
        self.lons = self.netcdf.groups['geolocation_data']['longitude'][:].data.astype(numpy.double)

    def read_gring(self):
        self.gring_lats = self.netcdf.GRingPointLatitude[::-1]
        self.gring_lons = self.netcdf.GRingPointLongitude[::-1]

    def get_cover_sids(self, cover_res):
        cover_sids = staremaster.conversions.gring2cover(self.gring_lats, self.gring_lons, cover_res)
        return cover_sids

    def create_sidecar(self, n_workers=1, cover_res=None, out_path=None):
        sids = staremaster.conversions.latlon2stare(lats=self.lats,
                                                    lons=self.lons,
                                                    resolution=None,
                                                    n_workers=n_workers,
                                                    adapt_resolution=True)

        if not cover_res:
            cover_res = staremaster.conversions.min_resolution(sids)
        cover_sids = self.get_cover_sids(cover_res)

        i = self.lats.shape[0]
        j = self.lats.shape[1]
        l = cover_sids.size

        sidecar = Sidecar(self.file_path, out_path)
        sidecar.write_dimensions(i, j, l, nom_res=self.nom_res)
        sidecar.write_lons(self.lons, nom_res=self.nom_res)
        sidecar.write_lats(self.lats, nom_res=self.nom_res)
        sidecar.write_sids(sids, nom_res=self.nom_res)
        sidecar.write_cover(cover_sids, nom_res=self.nom_res)
        return sidecar


class VNP03MOD(L2VIIRS):
    """ Also good for
        - VNP03DNB
        - VJ103MOD
        - VJ103DNB
    """

    def __init__(self, file_path):
        super(VNP03MOD, self).__init__(file_path)
        self.nom_res = '750m'


class VNP03IMG(L2VIIRS):
    """ Also good for
        - VJ103IMG
    """
    def __init__(self, file_path):
        super(VNP03IMG, self).__init__(file_path)
        self.nom_res = '375m'


class CLMDKS_L2_VIIRS(L2VIIRS):

    def __init__(self, file_path):
        super(CLMDKS_L2_VIIRS, self).__init__(file_path)
        self.nom_res = '750m'

