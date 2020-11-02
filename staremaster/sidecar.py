import netCDF4


class Sidecar:
    
    def __init__(self, granule_path, out_path=None):
        self.file_path = self.name_from_granule(granule_path, out_path)
        self.create()
        self.zlib = True
        self.shuffle = True
        
    def name_from_granule(self, granule_path, out_path):
        if out_path:
            return out_path + '.'.join(n.split('/')[-1].split('.')[0:-1]) + '_stare.nc'
        else:
            return  '.'.join(granule_path.split('.')[0:-1]) + '_stare.nc'
        
    def create(self):
        with netCDF4.Dataset(self.file_path, "w", format="NETCDF4") as rootgrp:
            pass
        
    def write_dimensions(self, i, j, l, nom_res):
        i_name = 'i_{nom_res}'.format(nom_res=nom_res)
        j_name = 'j_{nom_res}'.format(nom_res=nom_res)
        l_name = 'l_{nom_res}'.format(nom_res=nom_res)
        with netCDF4.Dataset(self.file_path , 'a', format="NETCDF4") as rootgrp:
            rootgrp.createDimension(i_name, i)
            rootgrp.createDimension(j_name, j)
            rootgrp.createDimension(l_name, l)

    def write_lons(self, lons, nom_res):
        i = lons.shape[0]
        j = lons.shape[1]
        varname = 'Longitude_{nom_res}'.format(nom_res=nom_res)
        i_name = 'i_{nom_res}'.format(nom_res=nom_res)
        j_name = 'j_{nom_res}'.format(nom_res=nom_res)        
        with netCDF4.Dataset(self.file_path , 'a', format="NETCDF4") as rootgrp:
            lons_netcdf = rootgrp.createVariable(varname=varname, 
                                                 datatype='f4', 
                                                 dimensions=(i_name, j_name),
                                                 chunksizes=[i, j],
                                                 shuffle=self.shuffle,
                                                 zlib=self.zlib)
            lons_netcdf.long_name = 'longitude'
            lons_netcdf.units = 'degrees_east'
            lons_netcdf[:, :] = lons
    
    def write_lats(self, lats, nom_res):
        i = lats.shape[0]
        j = lats.shape[1]
        varname = 'Latitude_{nom_res}'.format(nom_res=nom_res)
        i_name = 'i_{nom_res}'.format(nom_res=nom_res)
        j_name = 'j_{nom_res}'.format(nom_res=nom_res)        
        with netCDF4.Dataset(self.file_path , 'a', format="NETCDF4") as rootgrp:
            lats_netcdf = rootgrp.createVariable(varname=varname, 
                                                 datatype='f4', 
                                                 dimensions=(i_name, j_name),
                                                 chunksizes=[i, j],
                                                 shuffle=self.shuffle,
                                                 zlib=self.zlib)
            lats_netcdf.long_name = 'latitude'
            lats_netcdf.units = 'degrees_north'
            lats_netcdf[:, :] = lats
        
    def write_sids(self, sids, nom_res):
        i = sids.shape[0]
        j = sids.shape[1]
        varname = 'STARE_index_{nom_res}'.format(nom_res=nom_res)
        i_name = 'i_{nom_res}'.format(nom_res=nom_res)
        j_name = 'j_{nom_res}'.format(nom_res=nom_res)        
        with netCDF4.Dataset(self.file_path , 'a', format="NETCDF4") as rootgrp:
            sids_netcdf = rootgrp.createVariable(varname=varname, 
                                         datatype='u8', 
                                         dimensions=(i_name, j_name),
                                         chunksizes=[i, j],
                                         shuffle=self.shuffle,
                                         zlib=self.zlib)
            sids_netcdf.long_name = 'SpatioTemporal Adaptive Resolution Encoding (STARE) index'
            sids_netcdf[:, :] = sids


    def write_cover(self, cover, nom_res):
        l = cover.size
        varname = 'STARE_cover_{nom_res}'.format(nom_res=nom_res)
        l_name = 'l_{nom_res}'.format(nom_res=nom_res)
        with netCDF4.Dataset(self.file_path , 'a', format="NETCDF4") as rootgrp:
            cover_netcdf = rootgrp.createVariable(varname=varname, 
                                                  datatype='u8', 
                                                  dimensions=(l_name),
                                                  chunksizes=[l],
                                                  shuffle=self.shuffle,
                                                  zlib=self.zlib)
            cover_netcdf.long_name = 'SpatioTemporal Adaptive Resolution Encoding (STARE) cover'
 
