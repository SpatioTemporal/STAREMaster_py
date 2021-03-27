import xarray
import dask
import pystare
import numpy


def latlon2stare_dask(lats, lons, resolution, workers, adapt_resolution=True):
    # should probably make chunk size dependent on the number of workers and lat/lon dimensions
    chunk_size = 500 
    lat_x = xarray.DataArray(lats, dims=['x', 'y']).chunk({'x': chunk_size})
    lon_x = xarray.DataArray(lons, dims=['x', 'y']).chunk({'x': chunk_size})
    with dask.distributed.Client(n_workers=workers) as client:            
        sids = xarray.apply_ufunc(pystare.from_latlon2D,
                                  lat_x,
                                  lon_x,
                                  dask='parallelized',
                                  kwargs={'adapt_resolution': adapt_resolution, 'resolution': resolution},
                                  output_dtypes=[numpy.int64])
        return numpy.array(sids)
    

def latlon2stare(lats, lons, resolution=27, workers=None, adapt_resolution=True):    
    if workers:
        sids = latlon2stare_dask(lats, lons, resolution, workers, adapt_resolution)
    else: 
        sids = pystare.from_latlon2D(lats, lons, resolution, adapt_resolution)
    return sids


def gring2cover(lats, lons, level): 
    lats = numpy.array(lats)
    lons = numpy.array(lons)
    sids = pystare.to_nonconvex_hull_range_from_latlon(lats, lons, int(level))
    return sids 


def sids2cover(sids):
    return None


def min_level(sids):
    return int(pystare.spatial_resolution(sids).min())

def max_level(sids):
    return int(pystare.spatial_resolution(sids).max())
