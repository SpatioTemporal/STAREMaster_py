import staremaster


def test_bad_mod09():
    # Let's just verify this does not crash
    file_path = 'tests/data/viirs/VNP03IMG.A2022308.1930.002.2022309041547.nc'
    granule = staremaster.products.viirsL2.VNP03IMG(file_path)
    granule.read_latlon()
    granule.read_gring()
    granule.create_sidecar(n_workers=1, cover_res=None, out_path=None)
