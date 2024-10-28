import os
from setuptools import setup, find_packages


with open("README.md", "r") as f:
    long_description = f.read()


# Function to read the version from version.py
def read_version():
    version_path = os.path.join(os.path.dirname(__file__), 'zacrostools', 'version.py')
    with open(version_path, 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


setup(
    name='zacrostools',
    version=read_version(),
    description='A collective of tools for the preparation of input files for ZACROS',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    url='https://github.com/hprats/ZacrosTools',
    download_url='https://github.com/hprats/ZacrosTools/archive/refs/tags/v1.01.tar.gz',
    author='Hector Prats',
    author_email='hpratsgarcia@gmail.com',
    keywords=['python', 'chemistry', 'KMC', 'ZACROS'],
    install_requires=['pandas', 'scipy']
)
