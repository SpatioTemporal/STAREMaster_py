#!/usr/bin/env/python
"""Installation script
"""


import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    
    
    
with open('requirements.txt') as f:
    install_requires = f.read().splitlines()
    
    
LONG_DESCRIPTION = """STAREMaster_py is the python implementation of STAREMaster. It is used to create sidecar files for a collection of remote sensing products"""


# get all data dirs in the datasets module
data_files = []
scripts=['create_sidecar_files.py']


setup(
    name="STAREMaster_py",
    version='0.1',
    description="Create STARE diecar files",
    license="MIT",
    author="Niklas Griessbaum",
    author_email="griessbaum@ucsb.edu",
    url="https://github.com/NiklasPhabian/STAREMaster_py",
    long_description=LONG_DESCRIPTION,
    packages=[
        "staremaster"
    ],
    scripts=['create_sidecar_files.py'],
    python_requires=">=3.5",
    install_requires=install_requires,
    test_suite='tests'
) 
