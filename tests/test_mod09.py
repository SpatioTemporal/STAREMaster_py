import staremaster


def test_bad_mod09():
    # Let's just verify this does not crash
    file_path = 'tests/data/mod09/MOD09.A2002299.0710.006.2015151173939.hdf'
    granule = staremaster.products.mod09.MOD09(file_path)
    granule.read_latlon()
    granule.read_gring()
    granule.create_sidecar(n_workers=1, cover_res=None, out_path=None)
