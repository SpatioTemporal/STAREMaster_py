#!/usr/bin/python3

import configparser 
import argparse
import xarray
import dask
import pystare
from sidecar import Sidecar
import products
import numpy

chunk_size = 500


def latlon2stare(lat, lon, workers):
    lat_x = xarray.DataArray(lat, dims=['x', 'y']).chunk({'x': chunk_size})
    lon_x = xarray.DataArray(lon, dims=['x', 'y']).chunk({'x': chunk_size})
    if workers:
        with dask.distributed.Client(n_workers=4) as client:            
            sids = xarray.apply_ufunc(pystare.from_latlon2D,
                                      lat_x,
                                      lon_x,
                                      dask='parallelized',
                                      kwargs={'adapt_resolution': True},
                                      output_dtypes=[numpy.int64])
            sids = numpy.array(sids)
    else: 
        sids = pystare.from_latlon2D(lat_x, lon_x, adapt_resolution=True)
        
    return sids


def gring2cover(lats, lons, level): 
    lats = numpy.array(lats)
    lons = numpy.array(lons)
    sids = pystare.to_nonconvex_hull_range_from_latlon(lats, lons, int(level))
    return sids


def create_sidecar_mod09(file_path, workers):
    mod09 = products.MOD09(file_path)    
    
    sids = latlon2stare(mod09.lats, mod09.lons, workers)
    
    cover_res = int(pystare.spatial_resolution(sids).max())
    cover_sids = gring2cover(mod09.gring_lats, mod09.gring_lons, cover_res)
    
    i = sids.shape[0]
    j = sids.shape[1]
    l = cover_sids.size 
    
    sidecar = Sidecar(file_path)
    sidecar.write_dimensions(i, j, l, nom_res='1km')
    
    sidecar.write_lons(mod09.lons, nom_res='1km')
    sidecar.write_lats(mod09.lats, nom_res='1km')
    sidecar.write_sids(sids, nom_res='1km')
    sidecar.write_cover(cover_sids, nom_res='1km')
    
    
def create_sidecar_vnp02DNB(file_path):
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Creates Sidecar Files')
    parser.add_argument('--folder', metavar='folder', nargs='?', type=str, 
                        help='the folder to create sidecars for')
    parser.add_argument('--file', metavar='folder', nargs='?', type=str, 
                        help='the file to create a sidecar for')
    parser.add_argument('--product', metavar='product', nargs='?', type=str, 
                        help='product (e.g. VNP02DNB, VNP03DNB, CLDMSK_L2_VIIRS_SNPP, VNP46A1, MOD09)')
    parser.add_argument('--workers', metavar='workers', nargs='?', type=int, 
                        help='product (e.g. VNP02DNB, VNP03DNB, CLDMSK_L2_VIIRS_SNPP, VNP46A1, MOD09)')
    parser.add_argument('--catalogue', dest='catalogue', action='store_true')
    
    parser.set_defaults(day=True)    
    args = parser.parse_args()   

    if args.product is None:
        print('Wrong usage; need to specify the product \n')
        print(parser.print_help())
        quit()   
    
    if (args.folder is None and args.file is None):
        print('Wrong usage; need to specify a folder or a file \n')
        print(parser.print_help())
        quit()
        
    if args.product == 'MOD09' and args.file:
        create_sidecar_mod09(args.file, workers=args.workers)
        
        
        
    
    
