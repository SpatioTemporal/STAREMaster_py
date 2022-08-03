import numpy
import pystare
import pickle
import os
from staremaster.sidecar import Sidecar


class IMERG:
    
    def __init__(self):
        ## IMERG is a gridded dataset on a 0.05 degree grid
        self.lats = None
        self.lons = None
        self.nom_res = ''
        self.sids = []
        
    def get_latlon(self):
        self.lats = numpy.ascontiguousarray(numpy.tile(numpy.arange(-89.95, 90, 0.1), (3600, 1)).transpose())
        self.lons = numpy.tile(numpy.arange(-179.95, 180, 0.1), (1800, 1))

    def get_cover_sids(self):
        cover_sids = numpy.array([0x0000000000000000, 0x0800000000000000, 0x1000000000000000, 0x1800000000000000,
                                  0x2000000000000000, 0x2800000000000000, 0x3000000000000000, 0x3800000000000000])
        return cover_sids
    
    def load_sids_pickle(self, pickle_name='imerg_sids.pickle'):        
        with open(pickle_name, 'rb') as picke_file:
            self.sids = pickle.load(picke_file)
            
    def save_sids_pickle(self, pickle_name='imerg_sids.pickle'):        
        with open(pickle_name, 'wb') as picke_file:
            pickle.dump(self.sids, picke_file)
    
    def make_sids(self):    
        self.sids = pystare.from_latlon_2d(self.lats, self.lons, adapt_level=True)
    
    def get_sids(self):
        pickle_name = 'imerg_sids.pickle'
        if os.path.exists(pickle_name):
            self.load_sids_pickle(pickle_name)
        else:
            self.make_sids()
        return self.sids

    def create_sidecar(self, out_path):
        sids = self.get_sids()
        cover_sids = self.get_cover_sids()
        
        i = self.lats.shape[0]
        j = self.lats.shape[1]
        l = cover_sids.size
        
        sidecar = Sidecar(granule_path='IMERG.HDF5', out_path=out_path)
        sidecar.write_dimensions(i, j, l, nom_res=self.nom_res)    
        sidecar.write_sids(sids, nom_res=self.nom_res)
        sidecar.write_cover(cover_sids, nom_res=self.nom_res)
