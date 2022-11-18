import netCDF4
import numpy
from staremaster.sidecar import Sidecar
import staremaster.conversions
import pystare


class XCAL:

    scans = []

    def __init__(self, file_path):
        self.file_path = file_path
        self.netcdf = netCDF4.Dataset(file_path, 'r', format='NETCDF4')
        self.lats = {}
        self.lons = {}

    def load(self):
        self.get_latlon()

    def get_latlon(self):
        for scan in self.scans:
            self.lats[scan] = self.netcdf.groups[scan]['Latitude'][:].data.astype(numpy.double)
            self.lons[scan] = self.netcdf.groups[scan]['Longitude'][:].data.astype(numpy.double)

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
        sidecar.write_dimension('l', cover_all.size)
        sidecar.write_cover(cover_all, nom_res=nom_res)

        return sidecar

