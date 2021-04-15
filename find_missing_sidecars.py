#!/usr/bin/python3

import requests
import time
import glob
import os
import fnmatch
import xml
import xml.etree.ElementTree as ET
import argparse
import netCDF4
import sys


def companion_missing(granule_name, companion_names, granule_pattern):
    name_trunk = granule_name.split('.')[0:-1] #only remove .nc
    pattern = '.'.join(name_trunk) + _stare.nc #create full file name with _stare.nc
    companion_name = fnmatch.filter(companion_names, pattern)
    if len(companion_name) == 0:
        return True

def get_lonely_granules(granule_folder, companion_folder, granule_pattern):
    granule_names = []
    for file in glob.glob(os.path.expanduser(granule_folder) + granule_pattern + '*'):
        if file[-8:] != 'stare.nc':
            granule_names.append(file) #filter out stare files from granule
    granule_names = sorted(granule_names)    
    companion_names = sorted(glob.glob(os.path.expanduser(companion_folder) + '*' + '_stare.nc')) #switched wildcard order to call stare files
    missing = []
    for granule_name in granule_names:
        if companion_missing(granule_name, companion_names, granule_pattern):
            granule_name = granule_name.split('/')[-1]            
            missing.append(granule_name)
            print('missing companion for: ' + granule_name)
    return missing

def missing_variable(netcdf):
    variable_base = ['Longitude', 'Latitude', 'STARE_index', 'STARE_cover']
    for i in variable_base:
        name = [key for key in netcdf.variables.keys() if i in key]
        if len(name) == 0:
            return True
        

def find_missing_variables(companion_folder):
    companion_names = sorted(glob.glob(os.path.expanduser(companion_folder) + '*' + '_stare.nc')) #switched wildcard order to call stare files
    missing = []
    for companion_name in companion_names:
        netcdf = netCDF4.Dataset(companion_name, 'r', format = 'NETCDF4')
        if missing_variable(netcdf):
            companion_name = companion_name.split('/')[-1]
            missing.append(companion_name)
    return missing

        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Finds and retrieves missing geolocation companion files')
    parser.add_argument('--granule_folder', type=str, help='Granule folder (e.g. location of VNP02DNB, VNP03DNB, or CLDMSK)', required=True)
    parser.add_argument('--companion_folder', type=str, help='Companion folder (e.g. location of *_stare.nc). Default: granule_folder')
    parser.add_argument('--granule_pattern', type=str, help='Pattern of the granule name (e.g. VNP02DNB, VNP03DNB, or CLDMSK)', required=True)

    
    args = parser.parse_args()
   
    if args.companion_folder is None:
        args.companion_folder = args.granule_folder 
        
    lonely_granules = get_lonely_granules(granule_folder=args.granule_folder, companion_folder=args.companion_folder, 
                                          granule_pattern=args.granule_pattern)
    
    
    print('{n} missing companions'.format(n=len(lonely_granules)))
    
    missing_variables = find_missing_variables(companion_folder=args.companion_folder)
    
    print('{n} files are missing variables'.format(n=len(missing_variables)))
