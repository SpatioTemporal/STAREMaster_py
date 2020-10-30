#!/usr/bin/python3

import argparse
import xarray
import dask
import pystare
from sidecar import Sidecar
import products
import numpy


def latlon2stare(lats, lons, workers):
    # should probably make chunk size dependent on the number of workers and lat/lon dimensions
    chunk_size = 500 
    lat_x = xarray.DataArray(lats, dims=['x', 'y']).chunk({'x': chunk_size})
    lon_x = xarray.DataArray(lons, dims=['x', 'y']).chunk({'x': chunk_size})
    if workers:
        with dask.distributed.Client(n_workers=workers) as client:            
            sids = xarray.apply_ufunc(pystare.from_latlon2D,
                                      lat_x,
                                      lon_x,
                                      dask='parallelized',
                                      kwargs={'adapt_resolution': True},
                                      output_dtypes=[numpy.int64])
            sids = numpy.array(sids)
    else: 
        sids = pystare.from_latlon2D(lats, lons, adapt_resolution=True)
    return sids


def gring2cover(lats, lons, level): 
    lats = numpy.array(lats)
    lons = numpy.array(lons)
    sids = pystare.to_nonconvex_hull_range_from_latlon(lats, lons, int(level))
    return sids


def create_sidecar(file_path, workers, product, out_path, cover_res):
    if product == 'MOD09':
        create_sidecar_mod09(file_path, workers, out_path, cover_res)
    elif product == 'VNP03DNB':
        create_sidecar_vnp03dnb(file_path, workers, out_path, cover_res)
    else:        
        print('product not supported')
        quit()


def create_sidecar_mod09(file_path, workers, out_path, cover_res):
    mod09 = products.MOD09(file_path)    
    
    sids = latlon2stare(mod09.lats, mod09.lons, workers)
    
    if not cover_res:
        cover_res = int(pystare.spatial_resolution(sids).min())
        
    cover_sids = gring2cover(mod09.gring_lats, mod09.gring_lons, cover_res)
    
    i = sids.shape[0]
    j = sids.shape[1]
    l = cover_sids.size 
    
    sidecar = Sidecar(file_path, out_path)
    nom_res = '1km'
    sidecar.write_dimensions(i, j, l, nom_res=nom_res)    
    sidecar.write_lons(mod09.lons, nom_res=nom_res)
    sidecar.write_lats(mod09.lats, nom_res=nom_res)
    sidecar.write_sids(sids, nom_res=nom_res)
    sidecar.write_cover(cover_sids, nom_res=nom_res)
    
    
def create_sidecar_vnp03dnb(file_path, workers, out_path, cover_res):
    vnp03 = products.VNP03DNB(file_path)
    
    sids = latlon2stare(vnp03.lats, vnp03.lons, workers)
    
    cover_res = int(pystare.spatial_resolution(sids).min())
    cover_sids = gring2cover(vnp03.gring_lats, vnp03.gring_lons, cover_res)
    
    i = vnp03.lats.shape[0]
    j = vnp03.lats.shape[1]
    l = cover_sids.size
    
    sidecar = Sidecar(file_path, out_path)
    nom_res = '750m'
    sidecar.write_dimensions(i, j, l, nom_res=nom_res)    
    sidecar.write_lons(vnp03.lons, nom_res=nom_res)
    sidecar.write_lats(vnp03.lats, nom_res=nom_res)
    sidecar.write_sids(sids, nom_res=nom_res)
    sidecar.write_cover(cover_sids, nom_res=nom_res)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Creates Sidecar Files')
    parser.add_argument('--folder', metavar='folder', nargs='?', type=str, 
                        help='the folder to create sidecars for')
    parser.add_argument('--out_path', metavar='out_path', nargs='?', type=str, 
                        help='the folder to create sidecars in; default: next to granule')
    parser.add_argument('--file', metavar='file', nargs='?', type=str, 
                        help='the file to create a sidecar for')
    parser.add_argument('--product', metavar='product', nargs='?', type=str, 
                        help='product (e.g. VNP03DNB, MOD09)')
    parser.add_argument('--cover_res', metavar='cover_res', nargs='?', type=int, 
                        help='max STARE resolution of the cover. Default: min resolution of iFOVs')    
    parser.add_argument('--workers', metavar='n_workers', nargs='?', type=int, 
                        help='use n_workers (local) dask workers')
    parser.add_argument('--catalogue', dest='catalogue', action='store_true',
                        help='toggle creating a catalogue')
    parser.add_argument('--overwrite', dest='overwrite', action='store_true',
                        help='overwrite sidecar if file with same name exists (default: True)')
    
    parser.set_defaults(catalogue=False)    
    parser.set_defaults(overwrite=True)        
    args = parser.parse_args()   

    if args.product is None:
        print('Wrong usage; need to specify the product \n')
        print(parser.print_help())
        quit()   
    
    if (args.folder is None and args.file is None):
        print('Wrong usage; need to specify a folder or a file \n')
        print(parser.print_help())
        quit()
            
    if args.file:
        create_sidecar(file_path=args.file, 
                       workers=args.workers, 
                       product=args.product,
                       out_path=args.out_path,
                       cover_res=args.cover_res)
        
        
        
    
    
