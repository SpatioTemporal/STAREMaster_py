import netCDF4


class Sidecar:
    
    def __init__(self, granule_path, out_path=None):
        self.file_path = self.name_from_granule(granule_path, out_path)
        self.create()
        self.zlib = True
        self.shuffle = True
        
    def name_from_granule(self, granule_path, out_path):
        if out_path:
            return out_path + '.'.join(granule_path.split('/')[-1].split('.')[0:-1]) + '_stare.nc'
        else:
            return '.'.join(granule_path.split('.')[0:-1]) + '_stare.nc'
        
    def create(self):
        with netCDF4.Dataset(self.file_path, "w", format="NETCDF4") as rootgrp:
            pass
        
    def write_dimension(self, name, length, group=None):
        with netCDF4.Dataset(self.file_path , 'a', format="NETCDF4") as rootgrp:
            if group:
                grp = rootgrp.createGroup(group)
            else:
                grp = rootgrp
            grp.createDimension(name, length)
        
    def write_dimensions(self, i, j, l, nom_res=None, group=None):
        i_name = 'i'
        j_name = 'j'
        if nom_res:
            i_name += '_{nom_res}'.format(nom_res=nom_res)
            j_name += '_{nom_res}'.format(nom_res=nom_res)
        with netCDF4.Dataset(self.file_path, 'a', format="NETCDF4") as rootgrp:
            if group:
                grp = rootgrp.createGroup(group)
            else:
                grp = rootgrp
            grp.createDimension(i_name, i)
            grp.createDimension(j_name, j)

    def write_lons(self, lons, nom_res=None, group=None, fill_value=None):
        i = lons.shape[0]
        j = lons.shape[1]
        varname = 'Longitude'
        i_name = 'i'
        j_name = 'j'
        if nom_res:
            varname += '_{nom_res}'.format(nom_res=nom_res)
            i_name += '_{nom_res}'.format(nom_res=nom_res)
            j_name += '_{nom_res}'.format(nom_res=nom_res)
        with netCDF4.Dataset(self.file_path, 'a', format="NETCDF4") as rootgrp:
            if group:
                grp = rootgrp.createGroup(group)
            else:
                grp = rootgrp            
            lons_netcdf = grp.createVariable(varname=varname, 
                                             datatype='f4', 
                                             dimensions=(i_name, j_name),
                                             chunksizes=[i, j],
                                             shuffle=self.shuffle,
                                             zlib=self.zlib,
                                             fill_value=fill_value)
            lons_netcdf.long_name = 'Longitude'
            lons_netcdf.units = 'degrees_east'
            lons_netcdf[:, :] = lons
    
    def write_lats(self, lats, nom_res=None, group=None, fill_value=None):
        i = lats.shape[0]
        j = lats.shape[1]
        varname = 'Latitude'
        i_name = 'i'
        j_name = 'j'
        if nom_res:
            varname += '_{nom_res}'.format(nom_res=nom_res)
            i_name += '_{nom_res}'.format(nom_res=nom_res)
            j_name += '_{nom_res}'.format(nom_res=nom_res)
        with netCDF4.Dataset(self.file_path, 'a', format="NETCDF4") as rootgrp:
            if group:
                grp = rootgrp.createGroup(group)
            else:
                grp = rootgrp    
            lats_netcdf = grp.createVariable(varname=varname, 
                                             datatype='f4', 
                                             dimensions=(i_name, j_name),
                                             chunksizes=[i, j],
                                             shuffle=self.shuffle,
                                             zlib=self.zlib,
                                             fill_value=fill_value)
            lats_netcdf.long_name = 'Latitude'
            lats_netcdf.units = 'degrees_north'
            lats_netcdf[:, :] = lats            
        
    def write_sids(self, sids, nom_res=None, group=None, fill_value=-1):
        i = sids.shape[0]
        j = sids.shape[1]
        varname = 'STARE_index'.format(nom_res=nom_res)
        i_name = 'i'
        j_name = 'j'
        if nom_res:
            varname += '_{nom_res}'.format(nom_res=nom_res)
            i_name += '_{nom_res}'.format(nom_res=nom_res)
            j_name += '_{nom_res}'.format(nom_res=nom_res)   
        with netCDF4.Dataset(self.file_path, 'a', format="NETCDF4") as rootgrp:
            if group:
                grp = rootgrp.createGroup(group)
            else:
                grp = rootgrp    
            sids_netcdf = grp.createVariable(varname=varname, 
                                             datatype='u8', 
                                             dimensions=(i_name, j_name),
                                             chunksizes=[i, j],
                                             shuffle=self.shuffle,
                                             zlib=self.zlib,
                                             fill_value=fill_value)
            sids_netcdf.long_name = 'SpatioTemporal Adaptive Resolution Encoding (STARE) index'
            sids_netcdf[:, :] = sids

    def write_cover(self, cover, nom_res=None, group=None, fill_value=None):
        l = cover.size
        varname = 'STARE_cover'
        l_name = 'l'

        with netCDF4.Dataset(self.file_path, 'a', format="NETCDF4") as rootgrp:
            if group:
                grp = rootgrp.createGroup(group)
            else:
                grp = rootgrp
            grp.createDimension(l_name, l)
            cover_netcdf = grp.createVariable(varname=varname, 
                                              datatype='u8', 
                                              dimensions=(l_name),
                                              chunksizes=[l],
                                              shuffle=self.shuffle,
                                              zlib=self.zlib,
                                              fill_value=fill_value)
            cover_netcdf.long_name = 'SpatioTemporal Adaptive Resolution Encoding (STARE) cover'
            cover_netcdf[:] = cover
 
