import staremaster.conversions
from staremaster.products.hdfeos import HDFeos
from staremaster.sidecar import Sidecar
import numpy
import scipy.ndimage


class MOD09(HDFeos):
    
    def __init__(self, file_path):
        super(MOD09, self).__init__(file_path)
        self.read_laton()
        self.read_gring()
        self.nom_res = ['1km', '500m']
        
    def read_gring(self):
        core_metadata = self.get_metadata_group('CoreMetadata')    
        g_points = core_metadata['INVENTORYMETADATA']['SPATIALDOMAINCONTAINER']['HORIZONTALSPATIALDOMAINCONTAINER']['GPOLYGON']['GPOLYGONCONTAINER']['GRINGPOINT']        
        lats = g_points['GRINGPOINTLATITUDE']['VALUE']
        lons = g_points['GRINGPOINTLONGITUDE']['VALUE']
        self.gring_lats = list(map(float,lats.strip('()').split(', ')))[::-1]
        self.gring_lons = list(map(float, lons.strip('()').split(', ')))[::-1]

    def read_laton(self):
        self.lons['1km'] = self.hdf.select('Longitude').get().astype(numpy.double)
        self.lats['1km'] = self.hdf.select('Latitude').get().astype(numpy.double)
        self.get_500m_latlon()

    def get_500m_latlon(self):
        lat_500 = []
        lon_500 = []

        # Turns out they are not always 2030, but somtimes 2040 scans
        n_scans = self.lats['1km'].shape[0]

        for group_start in range(0, n_scans, 10):
            group_lats = self.lats['1km'][group_start:group_start + 10]
            group_lons = self.lons['1km'][group_start:group_start + 10]

            # Zoom out by factor (2n-1)/2; I.e. 2707/1354 in scan, 19/10 in track
            lat_500_g = scipy.ndimage.zoom(group_lats, (19 / 10, 2707 / 1354), order=1)
            lon_500_g = scipy.ndimage.zoom(group_lons, (19 / 10, 2707 / 1354), order=1)

            # Calculate the gradient to
            # a) shift 0.5 lenghts (250 m) in track direction and 1 length (500 m) in scan direction
            # b) Extrapolate the last observation in track direction
            gxx_lat, gyy_lat = numpy.gradient(lat_500_g)
            lat_500_g = lat_500_g - 0.5 * gxx_lat - 1 * gyy_lat
            lat_final = lat_500_g[-1] + 1 * gxx_lat[-1]  # Last row of group

            gxx_lon, gyy_lon = numpy.gradient(lon_500_g)
            lon_500_g = lon_500_g - 0.5 * gxx_lon - 1 * gyy_lon
            lon_final = lon_500_g[-1] + 1 * gxx_lon[-1]  # Last row of group

            lat_500_g = numpy.append(lat_500_g, [lat_final], axis=0)
            lon_500_g = numpy.append(lon_500_g, [lon_final], axis=0)

            lat_final_y = lat_500_g[:, -1] + numpy.gradient(lat_500_g)[1][:, -1]  # Last scan
            lat_500_g = numpy.append(lat_500_g.T, [lat_final_y], axis=0).T

            lon_final_y = lon_500_g[:, -1] + numpy.gradient(lon_500_g)[1][:, -1]  # Last scan
            lon_500_g = numpy.append(lon_500_g.T, [lon_final_y], axis=0).T

            lat_500.append(lat_500_g)
            lon_500.append(lon_500_g)

        self.lats['500m'] = numpy.concatenate(lat_500)
        self.lons['500m'] = numpy.concatenate(lon_500)


