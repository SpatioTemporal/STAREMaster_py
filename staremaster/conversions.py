import xarray
import dask
import pystare
import numpy
import distributed

# This is a workaround for https://github.com/dask/distributed/issues/4168
import multiprocessing.popen_spawn_posix


def latlon2stare_dask(lats, lons, resolution=None, workers=1, adapt_resolution=True):
    # should probably make chunk size dependent on the number of workers and lat/lon dimensions
    if resolution:
        adapt_resolution = False
    chunk_size = 500 
    lat_x = xarray.DataArray(lats, dims=['x', 'y']).chunk({'x': chunk_size})
    lon_x = xarray.DataArray(lons, dims=['x', 'y']).chunk({'x': chunk_size})
    with distributed.Client(n_workers=workers) as client:            
        sids = xarray.apply_ufunc(pystare.from_latlon2D,
                                  lat_x,
                                  lon_x,
                                  dask='parallelized',
                                  kwargs={'adapt_resolution': adapt_resolution, 'resolution': resolution},
                                  output_dtypes=[numpy.int64])
        return numpy.array(sids)
    

def latlon2stare(lats, lons, resolution=None, workers=None, adapt_resolution=True):    
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
    return dissolve()


def min_level(sids):
    return int(pystare.spatial_resolution(sids).min())


def max_level(sids):
    return int(pystare.spatial_resolution(sids).max())


def expand(sids):
    s_range = pystare.to_compressed_range(sids)
    expanded = pystare.expand_intervals(s_range  , -1, multi_resolution=True)
    return expanded 


def dissolve(sids, n_workers=1, n_chunks=1):
    sids = pystare.spatial_clear_to_resolution(sids)
    
    if isinstance(sids, list):
        dissolved = list(set(sids))
    elif isinstance(sids, numpy.ndarray):
        dissolved = numpy.unique(sids)
    else:
        return
    
    if n_workers==1 and n_chunks==1:
        dissolved = expand(dissolved)            
    else:
        dissolved = numpy.array_split(dissolved, n_workers)
        if n_workers > 1:
            with multiprocessing.Pool(processes=n_workers) as pool:
                dissolved = pool.map(dissolve, dissolved)
        else:
            dissolved = []
            for chunk in dissolved:
                dissolved.append(staremaster.conversions.dissolve(chunk))            
        dissolved = numpy.concatenate(dissolved)
        dissolved = numpy.unique(dissolved )
        dissolved = expand(dissolved)
        
    return dissolved
        
    
    

