import staremaster
import glob
import os
import netCDF4
import numpy


def test_make_sidecar():
    # Let's just verify this does not crash        
    file_path = 'tests/data/mod05/MOD05_L2.A2005349.2125.061.2017294065400.hdf'
    granule = staremaster.products.mod05.MOD05(file_path)
    granule.read_latlon()
    granule.read_gring()
    granule.create_sidecar(n_workers=1, cover_res=None, out_path=None)

    sidecar_path = 'tests/data/mod05/MOD05_L2.A2005349.2125.061.2017294065400_stare.nc'

    assert glob.glob(sidecar_path)

    netcdf = netCDF4.Dataset(sidecar_path, 'r', format='NETCDF4')
    sids = netcdf['STARE_index_5km'][:].data.astype(numpy.int64)
    assert sids[10, 10] == 4565555286659096141
    os.remove(sidecar_path)
        

