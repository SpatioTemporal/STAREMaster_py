#!/usr/bin/python3

import glob
import os
import argparse
import netCDF4
import re
import pandas


def get_granule_paths(folder, granule_pattern):
    granule_paths = sorted(glob.glob(os.path.expanduser(folder) + '/' + '*' ))
    pattern = '.*/{}.*[^_stare]\.(nc|hdf|HDF5)'.format(granule_pattern)
    granule_paths = list(filter(re.compile(pattern).match, granule_paths))        
    return granule_paths


def get_sidecar_paths(folder, granule_pattern):
    sidecar_paths = sorted(glob.glob(os.path.expanduser(folder) + '/' + '*' ))
    pattern = '.*/{}.*_stare\.(nc|hdf|HDF5)'.format(granule_pattern)
    sidecar_paths = list(filter(re.compile(pattern).match, sidecar_paths))       
    return sidecar_paths


def get_lonely_granules(granules, sidecars):    
    sidecars = [name.replace('_stare', '') for name in sidecars]
    missing = list(set(granules) - set(sidecars))
    return missing
    

def missing_variable(keys):
    keys = ';'.join(list(keys))
    variables = ['Longitude', 'Latitude', 'STARE_index', 'STARE_cover']
    for variable in variables:         
        if variable not in keys:            
            return True
    return False
        

def find_broken(sidecars):
    broken = []
    for sidecar in sidecars:
        netcdf = netCDF4.Dataset(sidecar, 'r', format = 'NETCDF4')
        keys = netcdf.variables.keys()
        if missing_variable(keys):
            granule = sidecar.replace('_stare', '')
            broken.append(granule)
    return broken

        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Finds and retrieves missing stare sidecar files')
    parser.add_argument('--granule_folder', type=str, help='Granule folder (e.g. location of VNP02DNB, VNP03DNB, or CLDMSK)', required=True)
    parser.add_argument('--sidecar_folder', type=str, help='Companion folder (e.g. location of *_stare.nc). Default: granule_folder', required=False)
    parser.add_argument('--granule_pattern', type=str, help='Pattern of the granule name (e.g. VNP02DNB, VNP03DNB, or CLDMSK)', required=False, default='')
    parser.add_argument('--find_broken', help='toggle if sidecars should be checked for completion', action='store_true')
    parser.add_argument('--archive', help='write an archive file out containing all granule-sidecar pairs')
    parser.add_argument('--out', help='file to write granules without sidecar')
    
    args = parser.parse_args()
   
    if args.sidecar_folder is None:
        args.sidecar_folder = args.granule_folder 
        
    
    granules = get_granule_paths(folder=args.granule_folder, granule_pattern=args.granule_pattern)
    sidecars = get_sidecar_paths(folder=args.sidecar_folder, granule_pattern=args.granule_pattern)
    
    print('{} granules'.format(len(granules)))
    print('{} sidecars'.format(len(sidecars)))
    
    missing = get_lonely_granules(granules, sidecars)
    print('{} missing'.format(len(missing)))
    
    if args.find_broken:    
        broken = find_broken(sidecars)
        missing = missing + broken        
        print('{} broken'.format(len(broken)))
    
    if args.out:    
        pandas.Series(missing).to_csv(args.out, index=False, header=False)
        
    if args.archive:
        good_sidecars = []
        good_granules = list(set(granules) - set(missing))
        for granule in good_granules:
            sidecar = '.'.join(granule.split('.')[0:-1]) + '_stare.' + granule.split('.')[-1]
            good_sidecars.append(sidecar)
        df = pandas.DataFrame({'granule': good_granules, 'sidecar': good_sidecars})
        df.to_csv(args.archive, header=False, index=False)
        
        
