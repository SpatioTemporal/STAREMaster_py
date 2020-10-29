class VNP02DNB:
    
    def __init__(self, file_path):
        self.netcdf = netCDF4.Dataset(file_path, 'r', format='NETCDF4')
        
    def read_latlon(self):
        self.lat = netcdf.groups['geolocation_data']['latitude'][:].data
        self.lon = netcdf.groups['geolocation_data']['longitude'][:].data
        
         
