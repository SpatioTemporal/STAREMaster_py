import os
import pytest
from staremaster.products.ssmis import SSMIS
import tempfile
import shutil


def test_ssmis_hdf5_support():
    """Test that SSMIS can handle HDF5 files."""
    # Use one of the test HDF5 files
    test_file = "tests/data/xcal/1C.F16.SSMIS.XCAL2016-V.20210201-S004436-E022630.089218.V05A.HDF5"
    
    if not os.path.exists(test_file):
        pytest.skip(f"Test file {test_file} not found")
    
    # Test that we can instantiate SSMIS with HDF5 file
    ssmis = SSMIS(test_file)
    
    # Test that file format is detected correctly
    assert ssmis.file_format == 'hdf5'
    
    # Test that we can load the data
    ssmis.load()
    
    # Test that we have the expected scans
    expected_scans = ['S1', 'S2', 'S3', 'S4']
    assert ssmis.scans == expected_scans
    
    # Test that we have latitude and longitude data for each scan
    for scan in expected_scans:
        assert scan in ssmis.lats
        assert scan in ssmis.lons
        assert ssmis.lats[scan] is not None
        assert ssmis.lons[scan] is not None
        assert ssmis.lats[scan].shape == ssmis.lons[scan].shape
    
    # Clean up
    del ssmis


def test_ssmis_hdf5_support_new_file():
    """Test that SSMIS can handle the new HDF5 file."""
    # Use the new test HDF5 file
    test_file = "tests/data/xcal/1C.F18.SSMIS.XCAL2021-V.20250105-S222535-E000725.078504.V07B.HDF5"
    
    if not os.path.exists(test_file):
        pytest.skip(f"Test file {test_file} not found")
    
    # Test that we can instantiate SSMIS with HDF5 file
    ssmis = SSMIS(test_file)
    
    # Test that file format is detected correctly
    assert ssmis.file_format == 'hdf5'
    
    # Test that we can load the data
    ssmis.load()
    
    # Test that we have the expected scans
    expected_scans = ['S1', 'S2', 'S3', 'S4']
    assert ssmis.scans == expected_scans
    
    # Test that we have latitude and longitude data for each scan
    for scan in expected_scans:
        assert scan in ssmis.lats
        assert scan in ssmis.lons
        assert ssmis.lats[scan] is not None
        assert ssmis.lons[scan] is not None
        assert ssmis.lats[scan].shape == ssmis.lons[scan].shape
    
    # Clean up
    del ssmis


def test_xcal_file_format_detection():
    """Test that file format detection works correctly."""
    from staremaster.products.xcal import XCAL
    
    # Test HDF5 file
    hdf5_file = "tests/data/xcal/1C.F16.SSMIS.XCAL2016-V.20210201-S004436-E022630.089218.V05A.HDF5"
    if os.path.exists(hdf5_file):
        xcal = XCAL(hdf5_file)
        assert xcal.file_format == 'hdf5'
        del xcal


def test_xcal_file_format_detection_new_file():
    """Test that file format detection works correctly for the new file."""
    from staremaster.products.xcal import XCAL
    
    # Test new HDF5 file
    hdf5_file = "tests/data/xcal/1C.F18.SSMIS.XCAL2021-V.20250105-S222535-E000725.078504.V07B.HDF5"
    if os.path.exists(hdf5_file):
        xcal = XCAL(hdf5_file)
        assert xcal.file_format == 'hdf5'
        del xcal


def test_ssmis_create_sidecar():
    """Test the create_sidecar function for the original SSMIS HDF5 file."""
    test_file = "tests/data/xcal/1C.F16.SSMIS.XCAL2016-V.20210201-S004436-E022630.089218.V05A.HDF5"
    if not os.path.exists(test_file):
        pytest.skip(f"Test file {test_file} not found")
    ssmis = SSMIS(test_file)
    ssmis.load()
    # Use a temporary directory for output
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "sidecar.nc")
        sidecar = ssmis.create_sidecar(out_path=out_path)
        assert sidecar is not None
        assert os.path.exists(sidecar.file_path)
        # Optionally, check file size > 0
        assert os.path.getsize(sidecar.file_path) > 0
    del ssmis


def test_ssmis_create_sidecar_new_file():
    """Test the create_sidecar function for the new SSMIS HDF5 file."""
    test_file = "tests/data/xcal/1C.F18.SSMIS.XCAL2021-V.20250105-S222535-E000725.078504.V07B.HDF5"
    if not os.path.exists(test_file):
        pytest.skip(f"Test file {test_file} not found")
    ssmis = SSMIS(test_file)
    ssmis.load()
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "sidecar.nc")
        sidecar = ssmis.create_sidecar(out_path=out_path)
        assert sidecar is not None
        assert os.path.exists(sidecar.file_path)
        assert os.path.getsize(sidecar.file_path) > 0
    del ssmis
