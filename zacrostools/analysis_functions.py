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
    dmatch = ['Number of gas species',
              'Gas species names',
              'Number of surface species',
              'Surface species names',
              'Total number of lattice sites',
              'Lattice surface area',
              'Site type names and total number of sites of that type']
    data = {}
    with open(f"{path}/general_output.txt", 'r') as file_object:
        line = file_object.readline()
        while len(dmatch) != 0:
            if 'Number of gas species' in line:
                data['n_gas_species'] = int(line.split()[-1])
                dmatch.remove('Number of gas species')
            if 'Gas species names' in line:
                data['gas_species_names'] = line.split(':')[-1].split()
                dmatch.remove('Gas species names')
            if 'Number of surface species' in line:
                data['n_surf_species'] = int(line.split()[-1])
                dmatch.remove('Number of surface species')
            if 'Surface species names' in line:
                data['surf_species_names'] = [ads[0:-1] for ads in line.split(':')[-1].split()]
                dmatch.remove('Surface species names')
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
    with open(f"{path}/specnum_output.txt", "r") as infile:
        header = infile.readline().split()
    full_data = np.loadtxt(f"{path}/specnum_output.txt", skiprows=1)
    index = np.where(full_data[:, 2] == find_nearest(full_data[:, 2], full_data[-1, 2] * ignore / 100))[0][0]
    data = np.delete(full_data, slice(0, index), 0)
    return data, header


def get_data_simulation(path):
    dmatch = ['pressure',
              'gas_specs_names',
              'gas_molar_fracs']
    data = {}
    with open(f"{path}/simulation_input.dat", 'r') as file_object:
        line = file_object.readline()
        while len(dmatch) != 0:
            if 'pressure' in line:
                data['pressure'] = float(line.split()[-1])
                dmatch.remove('pressure')
            if 'gas_specs_names' in line:
                data['gas_specs_names'] = line.split()[1:]
                dmatch.remove('gas_specs_names')
            if 'gas_molar_fracs' in line:
                data['gas_molar_fracs'] = [float(x) for x in line.split()[1:]]
                dmatch.remove('gas_molar_fracs')
            line = file_object.readline()
        return data
