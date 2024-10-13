from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='zacrostools',
    version='1.01',
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