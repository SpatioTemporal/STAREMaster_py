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
    name="staremaster",
    version='0.1.1',
    description="Create STARE sidecar files",
    license="MIT",
    author="Niklas Griessbaum",
    author_email="griessbaum@ucsb.edu",
    url="https://github.com/SpatioTemporal/STAREMaster_py",
    long_description=LONG_DESCRIPTION,
    packages=[
        "staremaster"
    ],
    scripts=scripts,
    #entry_points={'console_scripts': ['create_sidecar_files=create_sidecar_files:main']},
    python_requires=">=3.5",
    install_requires=install_requires,
    test_suite='tests'
) 
