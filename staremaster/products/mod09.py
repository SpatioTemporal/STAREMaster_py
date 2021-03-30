import staremaster.conversions
from staremaster.products.hdfeos import HDFeos
from staremaster.sidecar import Sidecar


class MOD09(HDFeos):
    
    def __init__(self, file_path):
        super(MOD09, self).__init__(file_path)
        self.read_laton()
        self.read_gring()
        self.nom_res = '1km'
        
    def read_gring(self):
        core_metadata = self.get_metadata_group('CoreMetadata')    
        g_points = core_metadata['INVENTORYMETADATA']['SPATIALDOMAINCONTAINER']['HORIZONTALSPATIALDOMAINCONTAINER']['GPOLYGON']['GPOLYGONCONTAINER']['GRINGPOINT']        
        lats = g_points['GRINGPOINTLATITUDE']['VALUE']
        lons = g_points['GRINGPOINTLONGITUDE']['VALUE']
        self.gring_lats = list(map(float,lats.strip('()').split(', ')))[::-1]
        self.gring_lons = list(map(float, lons.strip('()').split(', ')))[::-1]


