from staremaster.products.l2_viirs import L2_VIIRS


class VNP03DNB(L2_VIIRS):
    
    def __init__(self, file_path):
        super(VNP03DNB, self).__init__(file_path)
        self.nom_res = '750m'
        try:
            self.read_latlon()
            self.read_gring()
        except:
            print(file_path)   
