import netCDF4
import numpy
from staremaster.sidecar import Sidecar
import staremaster.conversions


class VNP03DNB:
    
    def __init__(self, file_path):
        self.netcdf = netCDF4.Dataset(file_path, 'r', format='NETCDF4')
        self.lats = None
        self.lons = None
        self.gring_lats = None
        self.gring_lon = None
        self.read_latlon()
        self.read_gring()
        
    def read_latlon(self):
        self.lats = self.netcdf.groups['geolocation_data']['latitude'][:].data.astype(numpy.double)
        self.lons = self.netcdf.groups['geolocation_data']['longitude'][:].data.astype(numpy.double)
        
    def read_gring(self):        
        self.gring_lats = self.netcdf.GRingPointLatitude[::-1]
        self.gring_lons = self.netcdf.GRingPointLongitude[::-1]
         

def create_sidecar(file_path, workers, cover_res, out_path):
    vnp03 = VNP03DNB(file_path)
    
    sids = staremaster.conversions.latlon2stare(lats=granule.lats, lons=granule.lons, resolution=-1, workers=workers, adapt_resolution=True)
    
    if not cover_res:
        cover_res = staremaster.conversions.min_level(sids)
    cover_sids = staremaster.conversions.gring2cover(vnp03.gring_lats, vnp03.gring_lons, cover_res)
    
    i = vnp03.lats.shape[0]
    j = vnp03.lats.shape[1]
    l = cover_sids.size
    
    nom_res = '750m'
    sidecar = Sidecar(file_path, out_path)
    sidecar.write_dimensions(i, j, l, nom_res=nom_res)    
    sidecar.write_lons(vnp03.lons, nom_res=nom_res)
    sidecar.write_lats(vnp03.lats, nom_res=nom_res)
    sidecar.write_sids(sids, nom_res=nom_res)
    sidecar.write_cover(cover_sids, nom_res=nom_res)
    return sidecar
