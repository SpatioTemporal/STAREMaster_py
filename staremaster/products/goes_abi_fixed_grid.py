import netCDF4
import numpy
from staremaster.sidecar import Sidecar
import staremaster.conversions
import pystare


# From: https://www.star.nesdis.noaa.gov/atmospheric-composition-training/python_abi_lat_lon.php
"""
This Python function can be used to calculate latitude and longitude from the GOES Imager Projection information in any ABI L1b or L2 data file.
Please acknowledge the NOAA/NESDIS/STAR Aerosols and Atmospheric Composition Science Team if using any of this code in your work/research
"""

# Calculate latitude and longitude from GOES ABI fixed grid projection data
# GOES ABI fixed grid projection is a map projection relative to the GOES satellite
# Units: latitude in °N (°S < 0), longitude in °E (°W < 0)
# See GOES-R Product User Guide (PUG) Volume 5 (L2 products) Section 4.2.8 for details & example of calculations
# "file_id" is an ABI L1b or L2 .nc file opened using the netCDF4 library

def calculate_degrees(file_id):
    
    # Ignore numpy errors for sqrt of negative number; occurs for GOES-16 ABI CONUS sector data
    # numpy.seterr(all='ignore')
    old_settings = numpy.seterr(all='ignore') #seterr to known value
    
    # Read in GOES ABI fixed grid projection variables and constants
    x_coordinate_1d = file_id.variables['x'][:].data.astype(numpy.double)  # E/W scanning angle in radians
    y_coordinate_1d = file_id.variables['y'][:].data.astype(numpy.double)  # N/S elevation angle in radians
    projection_info = file_id.variables['goes_imager_projection']
    lon_origin = projection_info.longitude_of_projection_origin
    H = projection_info.perspective_point_height+projection_info.semi_major_axis
    r_eq = projection_info.semi_major_axis
    r_pol = projection_info.semi_minor_axis
    
    # Create 2D coordinate matrices from 1D coordinate vectors
    x_coordinate_2d, y_coordinate_2d = numpy.meshgrid(x_coordinate_1d, y_coordinate_1d)
    
    # Equations to calculate latitude and longitude
    lambda_0 = (lon_origin*numpy.pi)/180.0  
    a_var = numpy.power(numpy.sin(x_coordinate_2d),2.0) + (numpy.power(numpy.cos(x_coordinate_2d),2.0)*(numpy.power(numpy.cos(y_coordinate_2d),2.0)+(((r_eq*r_eq)/(r_pol*r_pol))*numpy.power(numpy.sin(y_coordinate_2d),2.0))))
    b_var = -2.0*H*numpy.cos(x_coordinate_2d)*numpy.cos(y_coordinate_2d)
    c_var = (H**2.0)-(r_eq**2.0)
    r_s = (-1.0*b_var - numpy.sqrt((b_var**2)-(4.0*a_var*c_var)))/(2.0*a_var)
    s_x = r_s*numpy.cos(x_coordinate_2d)*numpy.cos(y_coordinate_2d)
    s_y = - r_s*numpy.sin(x_coordinate_2d)
    s_z = r_s*numpy.cos(x_coordinate_2d)*numpy.sin(y_coordinate_2d)
    
    abi_lat = (180.0/numpy.pi)*(numpy.arctan(((r_eq*r_eq)/(r_pol*r_pol))*((s_z/numpy.sqrt(((H-s_x)*(H-s_x))+(s_y*s_y))))))
    abi_lon = (lambda_0 - numpy.arctan(s_y/(H-s_x)))*(180.0/numpy.pi)
    
    numpy.seterr(**old_settings)  # reset to default
    
    return abi_lat, abi_lon


class GOES_ABI_FIXED_GRID:

    def __init__(self, file_path):
        self.file_path = file_path
        self.netcdf = netCDF4.Dataset(file_path, 'r', format='NETCDF4')
        self.lats = {}
        self.lons = {}
        self.mask = {}
        self.fill_value_in  = -9999
        self.fill_value_out = -998

    def load(self):
        self.get_latlon()


    def get_latlon(self):

        #old for scan in self.scans:
        #old     self.lats[scan] = self.netcdf.groups[scan]['Latitude'][:].data.astype(numpy.double)
        #old     self.lons[scan] = self.netcdf.groups[scan]['Longitude'][:].data.astype(numpy.double)

        lats,lons = calculate_degrees(self.netcdf)

        # Pixels off of the Earth
        mask = numpy.isnan(lons)
        lons[mask] = self.fill_value_in
        lats[mask] = self.fill_value_in

        # # Set to a fill value
        # # not_mask = ~mask
        # lons[mask] = self.fill_value
        # lats[mask] = self.fill_value
        # 
        # # Extend the edge id value to the edge of the array
        # ny  = lons.shape[0]
        # nx  = lons.shape[1]
        # nxo2 = int(nx/2)
        # idx = numpy.full([nx],False)
        # for j in range(ny):
        #     idx  = ~mask[j,:]
        #     
        #     idx0 = idx.copy(); idx0[nxo2:nx] = False
        #     lons[j,idx0] = numpy.amin(lons[j,idx])
        #     lats[j,idx0] = numpy.amin(lats[j,idx])
        #     
        #     idx1 = idx.copy(); idx1[0:nxo2]   = False
        #     lons[j,idx1] = numpy.amax(lons[j,idx])
        #     lats[j,idx1] = numpy.amax(lats[j,idx])

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

            # The following does not handle masked data or with weird fill values.
            # sids = staremaster.conversions.latlon2stare(lats, lons, n_workers=n_workers)
            
            sids = staremaster.conversions.latlon2stare(lats, lons, n_workers=n_workers,
                                                        fill_value_in  = self.fill_value_in,
                                                        fill_value_out = int(self.fill_value_out)
                                                        )

            not_mask = ~self.mask[resolution_name]

            # sids = numpy.full(lats.shape,self.fill_value,dtype=numpy.int64)
            # # Nope: sids[not_mask] = pystare.from_latlon(lats[not_mask],lons[not_mask],level=27)
            # 
            # # Too slow by a lot
            # for ix in range(sids.shape[1]):
            #     sids[not_mask[:,ix]] = staremaster.conversions.latlon2stare(
            #         lats[not_mask[:,ix]],
            #         lons[not_mask[:,ix]],
            #         n_workers=n_workers
            #         )

            if not cover_res:
                # Need to drop the resolution to make the cover less sparse
                cover_res = staremaster.conversions.min_resolution(sids[not_mask])
                cover_res = cover_res - 2
                if cover_res < 0:
                    cover_res = 0

            sids_adapted = pystare.spatial_coerce_resolution(sids[not_mask], cover_res)
            # sids_adapted = pystare.spatial_coerce_resolution(sids, cover_res)

            cover_sids = staremaster.conversions.merge_stare(sids_adapted, n_workers=n_workers)

            cover_all.append(cover_sids)

            i = lats.shape[0]
            j = lats.shape[1]
            l = cover_sids.size

            sids[self.mask[resolution_name]]=self.fill_value_out

            nom_res = None

            sidecar.write_dimensions(i, j, l, nom_res=nom_res, group=resolution_name)
            sidecar.write_lons(lons, nom_res=nom_res, group=resolution_name, fill_value=self.fill_value_in)
            sidecar.write_lats(lats, nom_res=nom_res, group=resolution_name, fill_value=self.fill_value_in)
            sidecar.write_sids(sids, nom_res=nom_res, group=resolution_name, fill_value=self.fill_value_out)
            sidecar.write_cover(cover_sids, nom_res=nom_res, group=resolution_name) # Should have no fill_value elements

        cover_all = numpy.concatenate(cover_all)
        cover_all = staremaster.conversions.merge_stare(cover_all, n_workers=n_workers)
        # sidecar.write_dimension('l', cover_all.size) # Already in the next call... since no group.
        sidecar.write_cover(cover_all, nom_res=nom_res)

        return sidecar

