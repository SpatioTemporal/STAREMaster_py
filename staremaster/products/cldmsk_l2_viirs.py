import netCDF4
import numpy
from staremaster.sidecar import Sidecar
import staremaster.conversions


class CLMDKS_L2_VIIRS:
    
    def __init__(self, file_path):
        self.netcdf = netCDF4.Dataset(file_path, 'r', format='NETCDF4')
        self.lats = None
        self.lons = None
        self.gring_lats = None
        self.gring_lon = None
        try:
            self.read_latlon()
            self.read_gring()
        except:
            print(file_path)            
        
    def read_latlon(self):
        self.lats = self.netcdf.groups['geolocation_data']['latitude'][:].data.astype(numpy.double)
        self.lons = self.netcdf.groups['geolocation_data']['longitude'][:].data.astype(numpy.double)
        
    def read_gring(self):        
        self.gring_lats = self.netcdf.GRingPointLatitude[::-1]
        self.gring_lons = self.netcdf.GRingPointLongitude[::-1]
         

def create_sidecar(file_path, workers=1, cover_res=None, out_path=None):
    granule = CLMDKS_L2_VIIRS(file_path)
    
    sids = staremaster.conversions.latlon2stare(lats=granule.lats, lons=granule.lons, resolution=-1, workers=workers, adapt_resolution=True)
    
    if not cover_res:
        cover_res = staremaster.conversions.min_level(sids)
    cover_sids = staremaster.conversions.gring2cover(granule.gring_lats, granule.gring_lons, cover_res)
    
    i = granule.lats.shape[0]
    j = granule.lats.shape[1]
    l = cover_sids.size
    
    nom_res = '750m'
    sidecar = Sidecar(file_path, out_path)
    sidecar.write_dimensions(i, j, l, nom_res=nom_res)    
    sidecar.write_lons(granule.lons, nom_res=nom_res)
    sidecar.write_lats(granule.lats, nom_res=nom_res)
    sidecar.write_sids(sids, nom_res=nom_res)
    sidecar.write_cover(cover_sids, nom_res=nom_res)
    return sidecar
