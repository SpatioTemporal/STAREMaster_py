import xarray
import pystare
import numpy
import distributed
import multiprocessing


# This is a workaround for https://github.com/dask/distributed/issues/4168
# import multiprocessing.popen_spawn_posix


def latlon2stare_dask(lats, lons, resolution=None, n_workers=1, adapt_resolution=True,
                      fill_value_in=None, fill_value_out=None
                      ):
    # should probably make chunk size dependent on the number of workers and lat/lon dimensions
    if resolution:
        adapt_resolution = False
    chunk_size = 500
    lat_x = xarray.DataArray(lats, dims=['x', 'y']).chunk({'x': chunk_size})
    lon_x = xarray.DataArray(lons, dims=['x', 'y']).chunk({'x': chunk_size})
    with distributed.Client(n_workers=n_workers) as client:
        sids = xarray.apply_ufunc(pystare.from_latlon_2d,
                                  lat_x,
                                  lon_x,
                                  dask='parallelized',
                                  kwargs={'adapt_level': adapt_resolution,
                                          'level': resolution,
                                          'fill_value_in': fill_value_in,
                                          'fill_value_out': fill_value_out
                                          },
                                  output_dtypes=[numpy.int64])
        return numpy.array(sids)


def latlon2stare(lats, lons, resolution=None, n_workers=1, adapt_resolution=True,
                 fill_value_in=None, fill_value_out=None
                 ):
    if n_workers > 1:
        sids = latlon2stare_dask(lats, lons, resolution, n_workers, adapt_resolution,
                                 fill_value_in=fill_value_in,
                                 fill_value_out=fill_value_out)
    else:
        sids = pystare.from_latlon_2d(lats, lons, resolution, adapt_resolution,
                                 fill_value_in=fill_value_in,
                                 fill_value_out=fill_value_out)
    return sids


def gring2cover(lats, lons, resolution):
    lats = numpy.array(lats)
    lons = numpy.array(lons)
    sids = pystare.cover_from_hull(lats, lons, int(resolution))
    return sids


def sids2cover(sids):
    return dissolve()


def min_resolution(sids):
    return int(pystare.spatial_resolution(sids).min())


def max_resolution(sids):
    return int(pystare.spatial_resolution(sids).max())


def dissolve(sids):
    s_range = pystare.to_compressed_range(sids)
    expanded = pystare.expand_intervals(s_range, -1, multi_resolution=True)
    return expanded


def merge_stare(sids, dissolve_sids=True, n_workers=1, n_chunks=1):
    sids = pystare.spatial_clear_to_resolution(sids)
    dissolved = numpy.unique(sids)

    if not dissolve_sids:
        return dissolved

    if n_workers == 1 and n_chunks == 1:
        tmp = dissolve(dissolved)
        dissolved = tmp
    else:
        if n_workers > 1:
            chunks = numpy.array_split(dissolved, n_workers)
            with multiprocessing.Pool(processes=n_workers) as pool:
                dissolved = pool.map(dissolve, chunks)
        elif n_chunks > 1:
            chunks = numpy.array_split(dissolved, n_chunks)
            dissolved = []
            for chunk in chunks:
                dissolved.append(dissolve(chunk))
        dissolved = numpy.concatenate(dissolved)
        dissolved = numpy.unique(dissolved)
        dissolved = dissolve(dissolved)

    return dissolved
