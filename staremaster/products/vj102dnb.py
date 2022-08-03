from staremaster.products.vnp02dnb import VNP02DNB
import glob


class VJ102DNB(VNP02DNB):
    
    def guess_companion_path(self):
        name_trunk = self.file_path.split('.')[0:-2]
        pattern = '.'.join(name_trunk).replace('VJ102DNB', 'VJ103DNB') + '*[!_stare].nc'
        companion_path = glob.glob(pattern)[0]
        return companion_path
