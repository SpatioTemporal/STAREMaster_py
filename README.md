This is a python implementation of STAREMaster.


# Install
No installer implemented yet

# Requirements

* pystare
* pyhdf
* numpy
* netCDF4
* argparse
* xarray
* dask

xarray and dask are hardcoded dependecies, but will become optional in the future

# Usage

```bash
usage: create_sidecar_files.py [-h] [--folder [folder]] [--out_path [out_path]] [--file [file]] [--product [product]] [--cover_res [cover_res]] [--workers [n_workers]] [--catalogue] [--overwrite]

Creates Sidecar Files

optional arguments:
  -h, --help            show this help message and exit
  --folder [folder]     the folder to create sidecars for
  --out_path [out_path]
                        the folder to create sidecars in; default: next to granule
  --file [file]         the file to create a sidecar for
  --product [product]   product (e.g. VNP03DNB, MOD09)
  --cover_res [cover_res]
                        max STARE resolution of the cover. Default: min resolution of iFOVs
  --workers [n_workers]
                        use n_workers (local) dask workers
  --catalogue           toggle creating a catalogue
  --overwrite           overwrite sidecar if file with same name exists (default: True)

```

e.g.

```bash
python3 create_sidecar_files.py --workers 4 --product MOD09 --file ~/MOD09.A2019317.0815.006.2019319020759.hdf
```

# Extension
To add support for additional products, we need the following:

1. a module in products/ containing a class for the product that implements the reading of the geolocation and the gring and an import of the module in products/__init__.py
2. a function that processes the creation of the sidecar file in create_sidecar_files.py
3. argument parsing for the added product


