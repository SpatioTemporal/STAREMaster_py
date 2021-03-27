#!/usr/bin/python3

import argparse
import staremaster.products
import glob
import multiprocessing
import itertools
import filelock
import pkgutil
import importlib


def create_sidecar(file_path, workers, product, cover_res, out_path, archive):

    if product is None:
        product = guess_product(file_path)

    if product == 'MOD09':
        sidecar = staremaster.products.mod09.create_sidecar(file_path, workers, cover_res, out_path)
    elif product == 'MOD05':
        sidecar = staremaster.products.mod05.create_sidecar(file_path, workers, cover_res, out_path)
    elif product == 'VNP03DNB':
        sidecar = staremaster.products.vnp03dnb.create_sidecar(file_path, workers, cover_res, out_path)
    elif product == 'VNP02DNB':
        sidecar = staremaster.products.vnp02dnb.create_sidecar(file_path, workers, cover_res, out_path)
    elif product == 'CLDMSK_L2_VIIRS':
        sidecar = staremaster.products.cldmsk_l2_viirs.create_sidecar(file_path, workers, cover_res, out_path)
    else:        
        print('product not supported')
        print('supported products are {}'.format(get_installed_products()))
        quit()
        
    if archive:
        with filelock.FileLock(archive + '.lock.'):        
            with open(archive, 'a') as cat:
                line = '{}, {} \n'.format(file_path, sidecar.file_path)
                cat.writelines(line)
                
    
def list_graunles(folder, product): 
    if product in ['MOD09', 'MOD05']:
        extension = 'hdf'
    elif product in ['VNP03DNB']:
        extension = 'nc'
        
    search_term = '{folder}{sep}{trunk}*[!_stare].{extension}'
    search_term = search_term.format(folder=folder, sep='/', trunk=product, extension=extension)
    return glob.glob(search_term)


def guess_product(file_path):
    file_name = file_path.split('/')[-1]
    if ('MOD05_L2' in file_path and '.hdf' in file_name):
        product = 'MOD05'
    elif ('MOD09.' in file_path and '.hdf' in file_name):
        product = 'MOD09'
    elif (('VNP03DNB' in file_path or 'VJ103DNB' in file_path) and '.nc' in file_name):
        product = 'VNP03DNB'
    elif (('VNP02DNB' in file_path or 'VJ102DNB' in file_path) and '.nc' in file_name):
        product = 'VNP02DNB'
    elif ('CLDMSK_L2_VIIRS' in file_path and '.nc' in file_name):
        product = 'CLDMSK_L2_VIIRS'        
    else:
        product = None
    return product
        
        
def remove_archived(file_paths, archive):    
    if glob.glob(archive):
        with open(archive, 'r') as cat:
            csv = cat.readlines()
        loaded_files = []
        for row in csv:
            loaded_files.append(row.split(',')[0])            
        print(loaded_files)
        print('Have been recorded in the archive and will not be processed')
        unprocessed = list(set(file_paths) - set(loaded_files))
    else:
        unprocessed = file_paths
    return unprocessed 


def get_installed_products():
    starmeaster_path = importlib.util.find_spec('staremaster.products').submodule_search_locations[0]
    products = [name for _, name, _ in pkgutil.iter_modules([starmeaster_path])]
    return products

        
if __name__ == '__main__':
    installed_products = get_installed_products()
    
    parser = argparse.ArgumentParser(description='Creates Sidecar Files')
    parser.add_argument('--folder', metavar='folder', type=str, 
                        help='the folder to create sidecars for')
    parser.add_argument('--files', metavar='files', nargs='+', type=str, 
                        help='the files to create a sidecar for')
    parser.add_argument('--out_path', metavar='out_path',  type=str, 
                        help='the folder to create sidecars in; default: next to granule')
    parser.add_argument('--product', metavar='product', type=str, 
                        help='product (e.g. VNP03DNB, MOD09, MOD05)',
                        choices=installed_products)
    parser.add_argument('--cover_res', metavar='cover_res', type=int, 
                        help='max STARE resolution of the cover. Default: min resolution of iFOVs')    
    parser.add_argument('--workers', metavar='n_workers', type=int, 
                        help='use n_workers (local) dask workers')
    parser.add_argument('--archive', metavar='archive',  type=str, 
                        help='''Create sidecars only for granules not listed in the archive file. 
                        Record all create sidecars and their corresponding granules in it.''')
    parser.add_argument('--parallel_files', dest='parallel_files', action='store_true',
                        help='Process files in parallel rather than looking up SIDs in parallel')
    
    parser.set_defaults(archive=False)    
    parser.set_defaults(parallel_files=False)    
    
    args = parser.parse_args()
        
    if args.files:
        file_paths = args.files       
    elif args.folder:
        file_paths = list_graunles(args.folder, product=args.product)
    else: 
        print('Wrong usage; need to specify a folder or a file \n')
        print(parser.print_help())
        quit()
        
    if args.archive:
        file_paths = remove_archived(file_paths, args.archive)

    if args.parallel_files:
        map_args = zip(file_paths, 
                       itertools.repeat(None),
                       itertools.repeat(args.product),
                       itertools.repeat(args.out_path),
                       itertools.repeat(args.cover_res),
                       itertools.repeat(args.archive))
        with multiprocessing.Pool(processes=args.workers) as pool:
            pool.starmap(create_sidecar, map_args)
    else:
        for file_path in file_paths:
            create_sidecar(file_path=file_path,
                           workers=args.workers,
                           product=args.product, 
                           out_path=args.out_path,
                           cover_res=args.cover_res,
                           archive=args.archive)
        
