import staremaster.conversions
from staremaster.products.hdfeos import HDFeos
from staremaster.sidecar import Sidecar


class MOD05(HDFeos):
    
    def __init__(self, file_path):
        super(MOD05, self).__init__(file_path)
        self.read_laton()
        self.read_gring()        
        
    def read_gring(self):
        core_metadata = self.get_metadata_group('ArchiveMetadata')    
        g_points = core_metadata['ARCHIVEDMETADATA']['GPOLYGON']['GPOLYGONCONTAINER']['GRINGPOINT']        
        lats = g_points['GRINGPOINTLATITUDE']['VALUE']
        lons = g_points['GRINGPOINTLONGITUDE']['VALUE']
        self.gring_lats = list(map(float,lats.strip('()').split(', ')))[::-1]
        self.gring_lons = list(map(float, lons.strip('()').split(', ')))[::-1]
        

def create_sidecar(file_path, workers, cover_res, out_path):
    nom_res = '5km'
    granule = MOD05(file_path)    
    
    sids = staremaster.conversions.latlon2stare(granule.lats, granule.lons, workers)
    
    if not cover_res:
        cover_res = staremaster.conversions.min_level(sids)
        
    cover_sids = staremaster.conversions.gring2cover(granule.gring_lats, granule.gring_lons, cover_res)
    
    i = sids.shape[0]
    j = sids.shape[1]
    l = cover_sids.size 
    
    sidecar = Sidecar(file_path, out_path)
    sidecar.write_dimensions(i, j, l, nom_res=nom_res)    
    sidecar.write_lons(granule.lons, nom_res=nom_res)
    sidecar.write_lats(granule.lats, nom_res=nom_res)
    sidecar.write_sids(sids, nom_res=nom_res)
    sidecar.write_cover(cover_sids, nom_res=nom_res)
    return sidecar
