#!/usr/bin/python3

import argparse
import products


def create_sidecar(file_path, workers, product, out_path, cover_res):
    if product == 'MOD09':
        products.mod09.create_sidecar(file_path, workers, out_path, cover_res)
    elif product == 'VNP03DNB':
        products.vnp03dnb.create_sidecar(file_path, workers, out_path, cover_res)
    else:        
        # Would be nice if we would a) catch this in main and b) if we could list the modules in products
        print('product not supported')
        quit()


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
        
        
        
    
    
