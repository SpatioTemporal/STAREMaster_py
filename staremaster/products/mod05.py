from staremaster.products.hdfeos import HDFeos
import numpy


class MOD05(HDFeos):
    
    def __init__(self, file_path):
        super(MOD05, self).__init__(file_path)
        self.nom_res = ['5km']

    def load(self):
        self.read_gring()
        self.read_latlon()

    def read_gring(self):
        core_metadata = self.get_metadata_group('ArchiveMetadata')    
        g_points = core_metadata['ARCHIVEDMETADATA']['GPOLYGON']['GPOLYGONCONTAINER']['GRINGPOINT']        
        lats = g_points['GRINGPOINTLATITUDE']['VALUE']
        lons = g_points['GRINGPOINTLONGITUDE']['VALUE']
        self.gring_lats = list(map(float, lats.strip('()').split(', ')))[::-1]
        self.gring_lons = list(map(float, lons.strip('()').split(', ')))[::-1]

    def read_latlon(self):
        self.lons['5km'] = self.read_ds('Latitude')
        self.lats['5km'] = self.read_ds('Latitude')
