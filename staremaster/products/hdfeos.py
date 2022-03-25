from pyhdf.SD import SD
import numpy
import staremaster
from staremaster.sidecar import Sidecar

 
def parse_hdfeos_metadata(string):
    out = {} 
    lines0 = [i.replace('\t','') for i in string.split('\n')]
    lines = []
    for line in lines0:
        if "=" in line:            
            key = line.split('=')[0]
            value = '='.join(line.split('=')[1:])
            lines.append(key.strip()+'='+value.strip())
        else:
            lines.append(line)
    i = -1
    while i<(len(lines))-1:        
        i+=1
        line = lines[i]
        if "=" in line:
            key = line.split('=')[0]
            value = '='.join(line.split('=')[1:])#.join('=')
            if key in ['GROUP', 'OBJECT']:
                endIdx = lines[i+1:].index('END_{}={}'.format(key, value))
                endIdx += i+1
                out[value] = parse_hdfeos_metadata("\n".join(lines[i+1:endIdx]))
                i = endIdx
            elif ('END_GROUP' not in key) and ('END_OBJECT' not in key):
                out[key] = str(value)
    return out


class HDFeos:
    
    def __init__(self, file_path):
        self.lats = None
        self.lons = None
        self.gring_lats = None
        self.gring_lons = None
        self.hdf = SD(file_path)
        self.file_path = file_path
        
    def read_laton(self):
        self.lons = self.hdf.select('Longitude').get().astype(numpy.double)
        self.lats = self.hdf.select('Latitude').get().astype(numpy.double)
        
    def get_metadata_group(self, group_name):
        metadata_group = {}
        keys = [s for s in self.hdf.attributes().keys() if group_name in s]
        for key in keys:    
            string = self.hdf.attributes()[key]
            m = parse_hdfeos_metadata(string)
            metadata_group = {**metadata_group, **m}
        return metadata_group
    
    def create_sidecar(self, n_workers, cover_res, out_path):
        sids = staremaster.conversions.latlon2stare(self.lats,
                                                    self.lons,
                                                    level=None,
                                                    n_workers=n_workers,
                                                    adapt_resolution=True)

        if not cover_res:
            cover_res = staremaster.conversions.min_level(sids)
            
        cover_sids = staremaster.conversions.gring2cover(self.gring_lats, self.gring_lons, cover_res)
        
        i = self.lats.shape[0]
        j = self.lats.shape[1]
        l = cover_sids.size
        
        sidecar = Sidecar(self.file_path, out_path)
        sidecar.write_dimensions(i, j, l, nom_res=self.nom_res)    
        sidecar.write_lons(self.lons, nom_res=self.nom_res)
        sidecar.write_lats(self.lats, nom_res=self.nom_res)
        sidecar.write_sids(sids, nom_res=self.nom_res)
        sidecar.write_cover(cover_sids, nom_res=self.nom_res)
        return sidecar

