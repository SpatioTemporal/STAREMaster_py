This is a python implementation of STAREMaster.


# Install

## With pip
The installer will install the create_sidecar_files.py script and its dependencies.

Create a virtualenv:

    mkvirtualevironment staremaster_py

The dependency pystare is not yet on pypi and therefore has to be installed e.g. from github:

    pip3 install git+https://github.com/NiklasPhabian/pystare.git
    
we then can install STAREMaster_py with 

    pip3 install -e STAREMaster_py/

    
## Conda

    conda create --name staremaster
    conda activate staremaster
    


# Requirements

* pystare
* pyhdf
* numpy
* netCDF4
* argparse
* xarray
* dask['distributed']
* filelock

xarray and dask are hardcoded dependecies, but will become optional in the future

# Usage

```

usage: create_sidecar_files.py [-h] [--folder folder] 
[--files files [files ...]] [--out_path out_path] 
[--product product] [--cover_res cover_res] [--workers n_workers] 
[--catalogue catalogue] [--parallel_files]

Creates Sidecar Files

optional arguments:
  -h, --help            show this help message and exit
  --folder folder       the folder to create sidecars for
  --files files [files ...]
                        the files to create a sidecar for
  --out_path out_path   the folder to create sidecars in; 
                        default: next to granule
  --product product     product (e.g. VNP03DNB, MOD09, MOD05)
  --cover_res cover_res
                        max STARE resolution of the cover.
                        Default: min resolution of iFOVs
  --workers n_workers   use n_workers (local) dask workers
  --catalogue catalogue
                        Create sidecars only for granules not 
                        listed in the archive file. 
                        Record all create sidecars and their
                        corresponding granules in it.


```

e.g.

```bash
python3 create_sidecar_files.py --workers 4 
       --product MOD09 --file ~/MOD09.A2019317.0815.006.2019319020759.hdf
```

# Extension
To add support for additional products, we need the following:

1. a module in products/ containing 
    * a class for the product that implements the reading of the geolocation and the gring 
    * a method that implements the write_sidecar() function
2. an import of the new module in products/\_\_init\_\_.py
3. argument parsing and switch for the added product in create_sidecar_files.py


