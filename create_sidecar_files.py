#!/usr/bin/python3

import argparse
import products
import glob
import pandas



def create_sidecar(file_path, workers, product, cover_res, out_path):
    if product == 'MOD09':
        sidecar = products.mod09.create_sidecar(file_path, workers, cover_res, out_path)
    elif product == 'MOD05':
        sidecar = products.mod05.create_sidecar(file_path, workers, cover_res, out_path)
    elif product == 'VNP03DNB':
        sidecar = products.vnp03dnb.create_sidecar(file_path, workers, cover_res, out_path)
    else:        
        # Would be nice if we would a) catch this in main and b) if we could list the modules in products
        print('product not supported')
        quit()
    return sidecar    
    
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
    elif ('VNP03DNB.' in file_path and '.nc' in file_name):
        product = 'VNP03DNB'
    else:
        product = None
    return product
        
        
def remove_skippable(file_paths, catalogue):
    file_paths = pandas.Series(file_paths)
    processed = pandas.read_csv(catalogue, header=None)[0]
    skip = file_paths.isin(list(processed))
    print('The following granules have been recorded in the archive and will not be processed')
    print(file_paths[skip==True])
    unprocessed = list(file_paths[skip==False])
    return unprocessed 
    
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Creates Sidecar Files')
    parser.add_argument('--folder', metavar='folder', type=str, 
                        help='the folder to create sidecars for')
    parser.add_argument('--out_path', metavar='out_path',  type=str, 
                        help='the folder to create sidecars in; default: next to granule')
    parser.add_argument('--files', metavar='files', nargs='+', type=str, 
                        help='the file to create a sidecar for')
    parser.add_argument('--product', metavar='product', type=str, 
                        help='product (e.g. VNP03DNB, MOD09)')
    parser.add_argument('--cover_res', metavar='cover_res', type=int, 
                        help='max STARE resolution of the cover. Default: min resolution of iFOVs')    
    parser.add_argument('--workers', metavar='n_workers', type=int, 
                        help='use n_workers (local) dask workers')
    parser.add_argument('--catalogue', metavar='catalogue',  type=str, 
                        help='Create sidecars only for granules not listed in the archive file. Record all create sidecars and their corresponding granules in it.')
    
    
    parser.set_defaults(catalogue=False)    
    parser.set_defaults(overwrite=True)        
    args = parser.parse_args()
        
    product = None
    if args.product is not None:
        product = args.product
  
    if args.files:
        file_paths = args.files       
    elif args.folder:
        file_paths = list_graunles(args.folder, product=product)
    else: 
        print('Wrong usage; need to specify a folder or a file \n')
        print(parser.print_help())
        quit()
        
    if args.catalogue:
        file_paths = remove_skippable(file_paths, args.catalogue)

    for file_path in file_paths:
        if args.product is None:
            product = guess_product(file_path)

        sidecar = create_sidecar(file_path=file_path,
                                 workers=args.workers,
                                 product=product, 
                                 out_path=args.out_path,
                                 cover_res=args.cover_res)
        
        if args.catalogue:
            with open(args.catalogue, 'a') as cat:
                line = '{}, {} \n'.format(file_path, sidecar.file_path)
                cat.writelines(line)
            
        
        
    
        
        
        
    
    
