import numpy as np


def find_nearest(array, value):
    """Finds the element of an array whose value is closest to a given value, and returns its index.

    Parameters
    ----------
    array: np.Array
    value: float

    Returns
    -------
    array[idx]: int

    """
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


def get_data_general(path):
    dmatch = ['Number of surface species',
              'Total number of lattice sites',
              'Lattice surface area',
              'Site type names and total number of sites of that type']
    data = {}
    with open(f"{path}/general_output.txt", 'r') as file_object:
        line = file_object.readline()
        while len(dmatch) != 0:
            if 'Number of surface species' in line:
                data['n_surf_species'] = int(line.split()[-1])
                dmatch.remove('Number of surface species')
            if 'Total number of lattice sites' in line:
                data['n_sites'] = int(line.split()[-1])
                dmatch.remove('Total number of lattice sites')
            if 'Lattice surface area' in line:
                data['area'] = float(line.split()[-1])
                dmatch.remove('Lattice surface area')
            if 'Site type names and total number of sites of that type' in line:
                line = file_object.readline()
                site_types = {}
                while line.strip():
                    num_sites_of_given_type = int(line.strip().split(' ')[1].replace('(', '').replace(')', ''))
                    site_types[line.strip().split(' ')[0]] = num_sites_of_given_type
                    line = file_object.readline()
                data['site_types'] = site_types
                dmatch.remove('Site type names and total number of sites of that type')
            line = file_object.readline()
        return data


def get_data_specnum(path, ignore=0.0):
    data_specnum = {'average': {}, 'tof': {}, 'kmc_time': 0.0}
    with open(f"{path}/specnum_output.txt", "r") as infile:
        header = infile.readline().split()
    full_data = np.loadtxt(f"{path}/specnum_output.txt", skiprows=1)
    index = np.where(full_data[:, 2] == find_nearest(full_data[:, 2], full_data[-1, 2] * ignore / 100))[0][0]
    data = np.delete(full_data, slice(0, index), 0)
    # Lattice energy
    data_specnum['average']['energy'] = np.average(data[:, 4])
    # Average number of adsorbed species
    i = 5
    while "*" in header[i]:
        data_specnum['average'][header[i].replace('*', '')] = np.average(data[:, i])
        i += 1
    # TOF in s-1
    for j in range(i, len(header)):
        if data[-1, j] < 0:
            data_specnum['tof'][header[j]] = float('NaN')
        elif data[-1, j] == 0:
            data_specnum['tof'][header[j]] = 0.00
        else:
            data_specnum['tof'][header[j]] = np.polyfit(data[:, 2], data[:, j], 1)[0]
    # KMC time
    data_specnum['kmc_time'] = data[-1, 2]
    return data_specnum


def get_selectivity(path, main_product, side_products, min_tof, ignore=0.0):   # min tof in s-1
    selectivity = float('NaN')
    data_specnum = get_data_specnum(path, ignore)
    tof_main_product = data_specnum['tof'][main_product]
    tof_side_products = 0.0
    for side_product in side_products:
        tof_side_products += data_specnum['tof'][side_product]
    if data_specnum['tof'][main_product] + tof_side_products > min_tof:
        selectivity = tof_main_product / (tof_main_product + tof_side_products) * 100
    return selectivity


def get_dominant_ads(path, ads_sites, ignore=0.0):
    dominant_ads_per_site = {'dominant_ads': {}, 'site_coverage': {}}
    data_general = get_data_general(path)
    data_specnum = get_data_specnum(path, ignore)
    site_types = list(data_general['site_types'])
    for i, site_type in enumerate(site_types):
        total_average = 0.0
        dominant_ads = None
        for ads in [ads for ads, site in ads_sites.items() if site == site_type]:
            total_average += data_specnum['average'][ads]
            if dominant_ads is None:
                dominant_ads = ads
            else:
                if data_specnum['average'][ads] > data_specnum['average'][dominant_ads]:
                    dominant_ads = ads
        site_coverage = total_average / data_general['site_types'][site_type] * 100
        dominant_ads_per_site['site_coverage'][site_type] = site_coverage
        dominant_ads_per_site['dominant_ads'][site_type] = dominant_ads
    return dominant_ads_per_site
