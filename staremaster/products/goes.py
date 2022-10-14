import netCDF4
import numpy
from staremaster.sidecar import Sidecar
import staremaster.conversions
import pystare

from pyproj import Proj

class GOES:

    def __init__(self, file_path):
        self.file_path = file_path
        self.netcdf = netCDF4.Dataset(file_path, 'r', format='NETCDF4')
        self.lats = {}
        self.lons = {}
        self.mask = {}
        self.fill_value = -9999

    def load(self):
        self.get_latlon()

    def get_latlon(self):

        #old for scan in self.scans:
        #old     self.lats[scan] = self.netcdf.groups[scan]['Latitude'][:].data.astype(numpy.double)
        #old     self.lons[scan] = self.netcdf.groups[scan]['Longitude'][:].data.astype(numpy.double)

        # Satellite height
        sat_h = self.netcdf.variables['goes_imager_projection'].perspective_point_height
        # Satellite longitude
        sat_lon = self.netcdf.variables['goes_imager_projection'].longitude_of_projection_origin
        # Satellite sweep
        sat_sweep = self.netcdf.variables['goes_imager_projection'].sweep_angle_axis
        # The projection x and y coordinates equals
        # the scanning angle (in radians) multiplied by the satellite height (http://proj4.org/projections/geos.html)
        X = self.netcdf.variables['x'][:][:] * sat_h
        Y = self.netcdf.variables['y'][:][:] * sat_h
        # map object with pyproj
        p = Proj(proj='geos', h=sat_h, lon_0=sat_lon, sweep=sat_sweep, a=6378137.0)
        # Convert map points to latitude and longitude with the magic provided by Pyproj
        XX, YY = numpy.meshgrid(X, Y)
        lons, lats = p(XX, YY, inverse=True)

        # Pixels outside the globe as self.fill_value (default -9999)
        mask = (lons == lons[0][0])
        
        # not_mask = ~mask
        lons[mask] = self.fill_value
        lats[mask] = self.fill_value

        ny  = lons.shape[0]
        nx  = lons.shape[1]
        nxo2 = int(nx/2)
        idx = numpy.full([nx],False)
        for j in range(ny):
            idx  = ~mask[j,:]
            
            idx0 = idx.copy(); idx0[nxo2:nx] = False
            lons[j,idx0] = numpy.amin(lons[j,idx])
            lats[j,idx0] = numpy.amin(lats[j,idx])
            
            idx1 = idx.copy(); idx1[0:nxo2]   = False
            lons[j,idx1] = numpy.amax(lons[j,idx])
            lats[j,idx1] = numpy.amax(lats[j,idx])

        resolution_name = self.netcdf.spatial_resolution.replace(' ','_')
        self.lons[resolution_name] = lons
        self.lats[resolution_name] = lats
        self.mask[resolution_name] = mask

        return

    def create_sidecar(self, n_workers=1, cover_res=None, out_path=None):

        sidecar = Sidecar(self.file_path, out_path)

        cover_all = []
        for resolution_name in self.lons.keys():
            lons = self.lons[resolution_name]
            lats = self.lats[resolution_name]
            sids = staremaster.conversions.latlon2stare(lats, lons, n_workers=n_workers)

            not_mask = ~self.mask[resolution_name]

            if not cover_res:
                # Need to drop the resolution to make the cover less sparse
                cover_res = staremaster.conversions.min_resolution(sids[not_mask])
                cover_res = cover_res - 2
                if cover_res < 0:
                    cover_res = 0

            print(1000)
            # sids_adapted = pystare.spatial_coerce_resolution(sids[not_mask], cover_res)
            sids_adapted = pystare.spatial_coerce_resolution(sids, cover_res)

            print(2000)
            cover_sids = staremaster.conversions.merge_stare(sids_adapted, n_workers=n_workers)

            print(3000)
            cover_all.append(cover_sids)

            i = lats.shape[0]
            j = lats.shape[1]
            l = cover_sids.size

            sids[self.mask[resolution_name]]=self.fill_value

            nom_res = None

            print(4000)
            sidecar.write_dimensions(i, j, l, nom_res=nom_res, group=resolution_name)
            sidecar.write_lons(lons, nom_res=nom_res, group=resolution_name)
            sidecar.write_lats(lats, nom_res=nom_res, group=resolution_name)
            sidecar.write_sids(sids, nom_res=nom_res, group=resolution_name)
            sidecar.write_cover(cover_sids, nom_res=nom_res, group=resolution_name)

        print(5000)
        cover_all = numpy.concatenate(cover_all)
        cover_all = staremaster.conversions.merge_stare(cover_all, n_workers=n_workers)
        sidecar.write_dimension('l', cover_all.size)
        sidecar.write_cover(cover_all, nom_res=nom_res)

        return sidecar

