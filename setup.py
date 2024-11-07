import os
import sys
from setuptools import setup, find_packages
from zacrostools.version import __version__

# Ensure the zacrostools package is accessible
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='zacrostools',
    version=__version__,
    description='A collection of tools for the preparation of input files for ZACROS',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    url='https://github.com/hprats/ZacrosTools',
    download_url=f'https://github.com/hprats/ZacrosTools/archive/refs/tags/v{__version__}.tar.gz',
    author='Hector Prats',
    author_email='hpratsgarcia@gmail.com',
    keywords=['python', 'chemistry', 'KMC', 'ZACROS'],
    install_requires=['pandas', 'scipy'],
    extras_require={
        'dev': ['pytest'],
    }
)
