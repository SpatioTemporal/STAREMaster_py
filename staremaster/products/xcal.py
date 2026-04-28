import netCDF4
import h5py
import numpy
from staremaster.sidecar import Sidecar
import staremaster.conversions
import pystare
import os


class XCAL:

    scans = []

    def __init__(self, file_path):
        self.file_path = file_path
        self.file_format = self._detect_file_format()
        self.data_file = self._open_file()
        self.lats = {}
        self.lons = {}

    def _detect_file_format(self):
        """Detect if the file is NetCDF4 or HDF5 based on extension and content."""
        file_ext = os.path.splitext(self.file_path)[1].lower()
        
        if file_ext in ['.nc', '.nc4', '.netcdf']:
            return 'netcdf4'
        elif file_ext in ['.he5', '.h5', '.hdf5', '.hdf']:
            return 'hdf5'
        else:
            # Try to detect by attempting to open with each format
            try:
                with netCDF4.Dataset(self.file_path, 'r') as test_file:
                    return 'netcdf4'
            except:
                try:
                    with h5py.File(self.file_path, 'r') as test_file:
                        return 'hdf5'
                except:
                    raise ValueError(f"Could not determine file format for {self.file_path}")

    def _open_file(self):
        """Open the file with the appropriate library."""
        if self.file_format == 'netcdf4':
            return netCDF4.Dataset(self.file_path, 'r', format='NETCDF4')
        elif self.file_format == 'hdf5':
            return h5py.File(self.file_path, 'r')
        else:
            raise ValueError(f"Unsupported file format: {self.file_format}")

    def load(self):
        self.get_latlon()

    def get_latlon(self):
        for scan in self.scans:
            if self.file_format == 'netcdf4':
                self.lats[scan] = self.data_file.groups[scan]['Latitude'][:].data.astype(numpy.double)
                self.lons[scan] = self.data_file.groups[scan]['Longitude'][:].data.astype(numpy.double)
            elif self.file_format == 'hdf5':
                self.lats[scan] = self.data_file[scan]['Latitude'][:].astype(numpy.double)
                self.lons[scan] = self.data_file[scan]['Longitude'][:].astype(numpy.double)

    def create_sidecar(self, n_workers=1, cover_res=None, out_path=None):

        sidecar = Sidecar(self.file_path, out_path)

        cover_all = []
        for scan in self.scans:
            lons = self.lons[scan]
            lats = self.lats[scan]
            sids = staremaster.conversions.latlon2stare(lats, lons, n_workers=n_workers)

            if not cover_res:
                # Need to drop the resolution to make the cover less sparse
                cover_res = staremaster.conversions.min_resolution(sids)
                cover_res = cover_res - 2
            # Clamp cover_res to [0, 27]
            cover_res = max(0, min(27, cover_res))

            sids_adapted = pystare.spatial_coerce_resolution(sids, cover_res)

            cover_sids = staremaster.conversions.merge_stare(sids_adapted, n_workers=n_workers)

            cover_all.append(cover_sids)

            i = lats.shape[0]
            j = lats.shape[1]
            l = cover_sids.size

            nom_res = None

            sidecar.write_dimensions(i, j, l, nom_res=nom_res, group=scan)
            sidecar.write_lons(lons, nom_res=nom_res, group=scan)
            sidecar.write_lats(lats, nom_res=nom_res, group=scan)
            sidecar.write_sids(sids, nom_res=nom_res, group=scan)
            sidecar.write_cover(cover_sids, nom_res=nom_res, group=scan)

        cover_all = numpy.concatenate(cover_all)
        cover_all = staremaster.conversions.merge_stare(cover_all, n_workers=n_workers)

        # Only create the 'l' dimension if it does not already exist
        with netCDF4.Dataset(sidecar.file_path, 'a', format='NETCDF4') as ncfile:
            if 'l' not in ncfile.dimensions:
                sidecar.write_dimension('l', cover_all.size)
        sidecar.write_cover(cover_all, nom_res=nom_res)

        return sidecar

    def __del__(self):
        """Clean up file handles when the object is destroyed."""
        if hasattr(self, 'data_file') and self.data_file is not None:
            try:
                self.data_file.close()
            except:
                pass

