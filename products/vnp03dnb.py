import netCDF4
import numpy


class VNP03DNB:
    
    def __init__(self, file_path):
        self.netcdf = netCDF4.Dataset(file_path, 'r', format='NETCDF4')
        self.lats = None
        self.lons = None
        self.gring_lats = None
        self.gring_lon = None
        self.read_latlon()
        self.read_gring()
        
    def read_latlon(self):
        self.lats = self.netcdf.groups['geolocation_data']['latitude'][:].data.astype(numpy.double)
        self.lons = self.netcdf.groups['geolocation_data']['longitude'][:].data.astype(numpy.double)
        
    def read_gring(self):        
        self.gring_lats = self.netcdf.GRingPointLatitude[::-1]
        self.gring_lons = self.netcdf.GRingPointLongitude[::-1]
         

