import netCDF4


class Sidecar:
    
    def __init__(self, granule_path):
        self.file_path = self.name_from_granule(granule_path)
        self.create()
        
    def name_from_granule(self, granule_path):
        return  '.'.join(granule_path.split('.')[0:-1]) + '_stare.nc'
        
    def create(self):
        with netCDF4.Dataset(self.file_path, "w", format="NETCDF4") as rootgrp:
            pass
        
    def write_dimensions(self, i, j, l, nom_res='1km'):
        i_name = 'i_'.format(nom_res)
        j_name = 'j_'.format(nom_res)
        l_name = 'l_'.format(nom_res)
        with netCDF4.Dataset(self.file_path , 'a', format="NETCDF4") as rootgrp:
            rootgrp.createDimension(i_name, i)
            rootgrp.createDimension(j_name, j)
            rootgrp.createDimension(l_name, l)

    def write_lons(self, lons, nom_res='1km'):
        i = lons.shape[0]
        j = lons.shape[1]
        varname = 'Longitude_{}'.format(nom_res)
        i_name = 'i_'.format(nom_res)
        j_name = 'j_'.format(nom_res)        
        with netCDF4.Dataset(self.file_path , 'a', format="NETCDF4") as rootgrp:
            lons_netcdf = rootgrp.createVariable(varname=varname, 
                                                 datatype='f8', 
                                                 dimensions=(i_name, j_name),
                                                 chunksizes=[i, j])
            lons_netcdf.long_name = 'latitude'
            lons_netcdf.units = 'degrees_east'
            lons_netcdf[:, :] = lons
    
    def write_lats(self, lats, nom_res='1km'):
        i = lats.shape[0]
        j = lats.shape[1]
        varname = 'Latitude_{}'.format(nom_res)
        i_name = 'i_'.format(nom_res)
        j_name = 'j_'.format(nom_res)        
        with netCDF4.Dataset(self.file_path , 'a', format="NETCDF4") as rootgrp:
            lats_netcdf = rootgrp.createVariable(varname=varname, 
                                                 datatype='f8', 
                                                 dimensions=(i_name, j_name),
                                                 chunksizes=[i, j])
            lats_netcdf.long_name = 'latitude'
            lats_netcdf.units = 'degrees_north'
            lats_netcdf[:, :] = lats
        
    def write_sids(self, sids, nom_res='1km'):
        i = sids.shape[0]
        j = sids.shape[1]
        varname = 'STARE_index_{}'.format(nom_res)
        i_name = 'i_'.format(nom_res)
        j_name = 'j_'.format(nom_res)        
        with netCDF4.Dataset(self.file_path , 'a', format="NETCDF4") as rootgrp:
            sids_netcdf = rootgrp.createVariable(varname=varname, 
                                         datatype='u8', 
                                         dimensions=(i_name, j_name),
                                         chunksizes=[i, j])
            sids_netcdf.long_name = 'SpatioTemporal Adaptive Resolution Encoding (STARE) index'
            sids_netcdf[:, :] = sids


    def write_cover(self, cover, nom_res='1km'):
        l = cover.size
        varname = 'STARE_cover_{}'.format(nom_res)
        l_name = 'l_'.format(nom_res)
        with netCDF4.Dataset(self.file_path , 'a', format="NETCDF4") as rootgrp:
            cover_netcdf = rootgrp.createVariable(varname=varname, 
                                                  datatype='u8', 
                                                  dimensions=(l_name),
                                                  chunksizes=[l])
            cover_netcdf.long_name = 'SpatioTemporal Adaptive Resolution Encoding (STARE) cover'
 
