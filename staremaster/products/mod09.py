from staremaster.products.hdfeos import HDFeos
import numpy
import scipy.ndimage
import copy


class MOD09(HDFeos):

    def __init__(self, file_path):
        super(MOD09, self).__init__(file_path)
        self.nom_res = ['1km', '500m']
        self.read_gring()

    def load(self):
        self.read_gring()
        self.read_latlon()

    def read_gring(self):
        core_metadata = self.get_metadata_group('CoreMetadata')
        g_points = \
        core_metadata['INVENTORYMETADATA']['SPATIALDOMAINCONTAINER']['HORIZONTALSPATIALDOMAINCONTAINER']['GPOLYGON'][
            'GPOLYGONCONTAINER']['GRINGPOINT']
        lats = g_points['GRINGPOINTLATITUDE']['VALUE']
        lons = g_points['GRINGPOINTLONGITUDE']['VALUE']
        self.gring_lats = list(map(float, lats.strip('()').split(', ')))[::-1]
        self.gring_lons = list(map(float, lons.strip('()').split(', ')))[::-1]

    def read_latlon(self):
        self.lons['1km'] = self.read_ds('Longitude')
        self.lats['1km'] = self.read_ds('Latitude')
        self.get_500m_latlon()

    def get_500m_latlon(self):
        lat_500 = []
        lon_500 = []

        # Turns out they are not always 2030, but somtimes 2040 scans
        n_scans = self.lats['1km'].shape[0]

        lats_1km = copy.copy(self.lats['1km'])
        lats_1km[lats_1km.mask] = numpy.nan
        lons_1km = copy.copy(self.lons['1km'])
        lons_1km[lons_1km.mask] = numpy.nan
        for group_start in range(0, n_scans, 10):
            group_lats = lats_1km[group_start:group_start + 10]
            group_lons = lons_1km[group_start:group_start + 10]

            # Zoom out by factor (2n-1)/2; I.e. 2707/1354 in scan, 19/10 in track
            lat_500_g = scipy.ndimage.zoom(group_lats, (19 / 10, 2707 / 1354), order=1)
            lon_500_g = scipy.ndimage.zoom(group_lons, (19 / 10, 2707 / 1354), order=1)

            # 1. Calculate the gradient
            # 2. shift 0.5 lengths (250 m) in track direction
            # 3. It is not obvious, but possibly also by 1 length (500 m) in scan direction.
            # This really depends on whether there is a timing offset for the first frame.
            # 4. Extrapolate the last observation in track direction
            # 5) Extrapolate the last observation in scan direction

            # First/x-axis is along-rack
            # Second/y-axis is along-scan

            gxx_lat, gyy_lat = numpy.gradient(lat_500_g)
            # lat_500_g = lat_500_g - 0.5 * gxx_lat - 1 * gyy_lat
            lat_500_g = lat_500_g - 0.5 * gxx_lat
            lat_final = lat_500_g[-1] + 1 * gxx_lat[-1]  # Last in track of group

            gxx_lon, gyy_lon = numpy.gradient(lon_500_g)
            # lon_500_g = lon_500_g - 0.5 * gxx_lon - 1 * gyy_lon
            lon_500_g = lon_500_g - 0.5 * gxx_lon
            lon_final = lon_500_g[-1] + 1 * gxx_lon[-1]  # Last in track of group

            lat_500_g = numpy.append(lat_500_g, [lat_final], axis=0)
            lon_500_g = numpy.append(lon_500_g, [lon_final], axis=0)

            lat_final_y = lat_500_g[:, -1] + numpy.gradient(lat_500_g)[1][:, -1]  # Last scan
            lat_500_g = numpy.append(lat_500_g.T, [lat_final_y], axis=0).T

            lon_final_y = lon_500_g[:, -1] + numpy.gradient(lon_500_g)[1][:, -1]  # Last scan
            lon_500_g = numpy.append(lon_500_g.T, [lon_final_y], axis=0).T

            lat_500.append(lat_500_g)
            lon_500.append(lon_500_g)

        lat_500 = numpy.concatenate(lat_500)
        lat_500 = numpy.ma.array(lat_500, mask=numpy.isnan(lat_500))
        self.lats['500m'] = lat_500

        lon_500 = numpy.concatenate(lon_500)
        lon_500 = numpy.ma.array(lon_500, mask=numpy.isnan(lon_500))
        self.lons['500m'] = lon_500
