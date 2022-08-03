import netCDF4
import numpy
from staremaster.sidecar import Sidecar
import staremaster.conversions
from staremaster.products.l2_viirs import L2_VIIRS


class CLMDKS_L2_VIIRS(L2_VIIRS):    
    
    def __init__(self, file_path):
        super(CLMDKS_L2_VIIRS, self).__init__(file_path)
        self.nom_res = '750m'

        
       
