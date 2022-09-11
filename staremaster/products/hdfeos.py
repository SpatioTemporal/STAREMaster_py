from pyhdf.SD import SD
import staremaster
from staremaster.sidecar import Sidecar
import numpy


def parse_hdfeos_metadata(string):
    out = {}
    lines0 = [i.replace('\t', '') for i in string.split('\n')]
    lines = []
    for line in lines0:
        if "=" in line:
            key = line.split('=')[0]
            value = '='.join(line.split('=')[1:])
            lines.append(key.strip() + '=' + value.strip())
        else:
            lines.append(line)
    i = -1
    while i < (len(lines)) - 1:
        i += 1
        line = lines[i]
        if "=" in line:
            key = line.split('=')[0]
            value = '='.join(line.split('=')[1:])  # .join('=')
            if key in ['GROUP', 'OBJECT']:
                endIdx = lines[i + 1:].index('END_{}={}'.format(key, value))
                endIdx += i + 1
                out[value] = parse_hdfeos_metadata("\n".join(lines[i + 1:endIdx]))
                i = endIdx
            elif ('END_GROUP' not in key) and ('END_OBJECT' not in key):
                out[key] = str(value)
    return out


class HDFeos:

    def __init__(self, file_path):
        self.lats = {}
        self.lons = {}
        self.gring_lats = None
        self.gring_lons = None
        self.hdf = SD(file_path)
        self.file_path = file_path
        self.nom_res = []
        self.sids = {}
        self.cover_sids = []

    def get_metadata_group(self, group_name):
        metadata_group = {}
        keys = [s for s in self.hdf.attributes().keys() if group_name in s]
        for key in keys:
            string = self.hdf.attributes()[key]
            m = parse_hdfeos_metadata(string)
            metadata_group = {**metadata_group, **m}
        return metadata_group

    def make_sids(self, n_workers):
        for res in self.nom_res:
            sids = staremaster.conversions.latlon2stare(self.lats[res], self.lons[res],
                                                        resolution=None, n_workers=n_workers, adapt_resolution=True)
            sids = numpy.ma.array(sids, mask=self.lats[res].mask, fill_value=-1)
            self.sids[res] = sids
            
    def get_cover_res_from_sids(self):
        sids = self.sids[self.nom_res[0]]
        sids = sids[sids.mask == False]
        cover_res = staremaster.conversions.min_resolution(sids)
        return cover_res

    def make_cover_sids(self, cover_res):
        if cover_res is None:
            # If we didn't get a cover resolution, we take the minimum of the iFOV resolutions
            cover_res = self.get_cover_res_from_sids()
        self.read_gring()
        self.cover_sids = staremaster.conversions.gring2cover(self.gring_lats, self.gring_lons, cover_res)

    def read_ds(self, sd_name):
        ds = self.hdf.select(sd_name)
        data = ds.get().astype(numpy.double)
        attributes = ds.attributes()
        # fill_value = attributes['_FillValue'] # is set to '0' in hdfeos ...
        valid_range = attributes['valid_range']
        lower_bound = valid_range[0]
        upper_bound = valid_range[1]
        data = numpy.ma.masked_outside(data, lower_bound, upper_bound, copy=True)
        return data

    def create_sidecar(self, n_workers, cover_res=None, out_path=None):
        self.make_sids(n_workers)
        try:
            self.make_cover_sids(cover_res)
        except ValueError as e:
            print('Failed to create sids/covers for {file_name}'.format(file_name=self.file_path))
            raise e

        sidecar = Sidecar(self.file_path, out_path)
        sidecar.write_cover(self.cover_sids, nom_res=self.nom_res)

        for res in self.nom_res:
            i = self.lats[res].shape[0]
            j = self.lats[res].shape[1]
            l = self.cover_sids.size
            sidecar.write_dimensions(i, j, l, nom_res=res)
            sidecar.write_lons(self.lons[res], nom_res=res)
            sidecar.write_lats(self.lats[res], nom_res=res)
            sidecar.write_sids(self.sids[res], nom_res=res)

        return sidecar
