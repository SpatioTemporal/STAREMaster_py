import netCDF4
import numpy


class SSMIS:
    
    def __init__(self, file_path):
        self.netcdf = netCDF4.Dataset(file_path, 'r', format='NETCDF4')
        self.lats = {}
        self.lons = {}
        self.gring_lats = {}
        self.gring_lon = {}
        self.read_latlon()
        
    def read_latlon(self):
        for scan in ['S1', 'S2', 'S3', 'S4']:
            self.lats[scan] = self.netcdf.groups[scan]['Latitude'][:].data.astype(numpy.double)
            self.lons[scan] = self.netcdf.groups[scan]['Longitude'][:].data.astype(numpy.double)
        

def write_group(group_name):
    pass

def create_sidecar(file_path, workers, cover_res, out_path):
    granule = SSMIS(file_path)
    sidecar = Sidecar(file_path, out_path)
    
    sids = {}
    for scan in ['S1', 'S2', 'S3', 'S4']:
        lons = granule.lons[scan]
        lats = granule.lats[scan]
        sids = staremaster.conversions.latlon2stare(lats, lons, workers)
    
        if not cover_res:
            cover_res = staremaster.conversions.min_level(sids)
        cover_sids = staremaster.conversions.sids2cover(sids, cover_res)
    
        i = lats.shape[0]
        j = lats.shape[1]
        l = cover_sids.size
    
        nom_res = None
        
        sidecar.write_dimensions(i, j, l, nom_res=nom_res, group=scan)    
        sidecar.write_lons(lons, nom_res=nom_res, group=scan)
        sidecar.write_lats(lats, nom_res=nom_res, group=scan)
        sidecar.write_sids(sids, nom_res=nom_res, group=scan)
        sidecar.write_cover(cover_sids, nom_res=nom_res, group=scan)
    
    return sidecar
