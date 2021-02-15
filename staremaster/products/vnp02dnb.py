import netCDF4
import numpy
from staremaster.sidecar import Sidecar
import staremaster.conversions
import glob
from staremaster.products.vnp03dnb import VNP03DNB


class VNP02DNB(VNP03DNB):
    
    def __init__(self, file_path):
        self.file_path = file_path
        vnp03_path = self.guess_vnp03path()
        self.netcdf = netCDF4.Dataset(vnp03_path, 'r', format='NETCDF4')
        self.lats = None
        self.lons = None
        self.gring_lats = None
        self.gring_lon = None
        self.read_latlon()
        self.read_gring()
    
    def guess_vnp03path(self):
        name_trunk = self.file_path.split('.')[0:-2]
        pattern = '.'.join(name_trunk).replace('VNP02DNB', 'VNP03DNB') + '*'
        vnp03_path = glob.glob(pattern)[0]
        return vnp03_path
                 

def create_sidecar(file_path, workers, cover_res, out_path):
    vnp03 = VNP02DNB(file_path)
    
    sids = staremaster.conversions.latlon2stare(vnp03.lats, vnp03.lons, workers)
    
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
