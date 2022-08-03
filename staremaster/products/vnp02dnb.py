import netCDF4
import glob
from staremaster.products.l2_viirs import L2_VIIRS


class VNP02DNB(L2_VIIRS):
    
    def __init__(self, file_path):
        super(VNP02DNB, self).__init__(file_path)        
        companion_path = self.guess_companion_path()
        self.netcdf = netCDF4.Dataset(companion_path, 'r', format='NETCDF4')
        self.nom_res = '750m'

    def guess_companion_path(self):
        name_trunk = self.file_path.split('.')[0:-2]
        pattern = '.'.join(name_trunk).replace('VNP02DNB', 'VNP03DNB') + '*[!_stare].nc'
        companion_path = glob.glob(pattern)[0]
        return companion_path
        
