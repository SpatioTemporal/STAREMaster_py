import unittest 
import staremaster
import glob
import os
import netCDF4
import numpy


class MainTest(unittest.TestCase):
    
    def test_make_sidecar(self):
        # Let's just verify this does not crash        
        file_path = 'tests/data/mod05/MOD05_L2.A2005349.2125.061.2017294065400.hdf'
        staremaster.products.mod05.create_sidecar(file_path, 
                                                  workers=None, 
                                                  cover_res=None, 
                                                  out_path=None)
        sidecar_path = 'tests/data/mod05/MOD05_L2.A2005349.2125.061.2017294065400_stare.nc'
        
        with self.subTest():
            self.assertTrue(glob.glob(sidecar_path))
        with self.subTest():
            netcdf = netCDF4.Dataset(sidecar_path, 'r', format='NETCDF4')
            sids = netcdf['STARE_index_5km'][:].data.astype(numpy.int64)
            self.assertTrue(sids[10,10] == 3461778018277136489)
        os.remove(sidecar_path)
         

def test_bad_mod09():
    pass