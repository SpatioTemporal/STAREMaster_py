import netCDF4
import numpy
from staremaster.sidecar import Sidecar
import staremaster.conversions
import pystare


class SSMIS:
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.netcdf = netCDF4.Dataset(file_path, 'r', format='NETCDF4')
        self.lats = {}
        self.lons = {}
        self.read_latlon()
        
    def read_latlon(self):
        for scan in ['S1', 'S2', 'S3', 'S4']:
            self.lats[scan] = self.netcdf.groups[scan]['Latitude'][:].data.astype(numpy.double)
            self.lons[scan] = self.netcdf.groups[scan]['Longitude'][:].data.astype(numpy.double)
        
    def write_group(group_name):
        pass

    def create_sidecar(self, workers=1, cover_res=None, out_path=None):
        
        sidecar = Sidecar(self.file_path, out_path)
    
        cover_all = []
        for scan in ['S1', 'S2', 'S3', 'S4']:
            lons = self.lons[scan]
            lats = self.lats[scan]
            sids = staremaster.conversions.latlon2stare(lats, lons, workers)
        
            if not cover_res:                
                cover_res = staremaster.conversions.min_level(sids)
                # Need to drop the resolution to make the cover less sparse
                cover_res = cover_res - 2
            
            sids_adapted = pystare.spatial_coerce_resolution(sids, cover_res)      
            sids_adapted = pystare.spatial_clear_to_resolution(sids_adapted )
            
            cover = staremaster.conversions.dissolve(sids_adapted, n_workers=workers)
            
            cover_all.append(cover)
        
            i = lats.shape[0]
            j = lats.shape[1]
            l = cover.size
        
            nom_res = None
            
            sidecar.write_dimensions(i, j, l, nom_res=nom_res, group=scan)    
            sidecar.write_lons(lons, nom_res=nom_res, group=scan)
            sidecar.write_lats(lats, nom_res=nom_res, group=scan)
            sidecar.write_sids(sids, nom_res=nom_res, group=scan)
            sidecar.write_cover(cover, nom_res=nom_res, group=scan)
        
        cover_all = numpy.concatenate(cover_all)
        cover_all  = staremaster.conversions.dissolve(cover_all, n_workers=workers)
        sidecar.write_dimension('l', cover_all.size)
        sidecar.write_cover(cover_all, nom_res=nom_res)
        
        return sidecar
