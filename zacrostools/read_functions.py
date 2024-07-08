import numpy as np
from zacrostools.calc_functions import find_nearest


def parse_general_output(path):
    dmatch = {
        'n_gas_species': 'Number of gas species:',
        'gas_species_names': 'Gas species names:',
        'n_surf_species': 'Number of surface species:',
        'surf_species_names': 'Surface species names:',
        'n_sites': 'Total number of lattice sites:',
        'area': 'Lattice surface area:',
        'site_types': 'Site type names and total number of sites of that type:'
    }
    data = {}
    num_matches = 0
    with open(f"{path}/general_output.txt", 'r') as file_object:
        line = file_object.readline()
        while num_matches < len(dmatch):
            for key, pattern in dmatch.items():
                if pattern in line:
                    if key in ['n_gas_species', 'n_surf_species', 'n_sites']:
                        data[key] = int(line.split()[-1])
                    elif key == 'gas_species_names':
                        data[key] = line.split(':')[-1].split()
                    elif key == 'surf_species_names':
                        data[key] = [ads[0:-1] for ads in line.split(':')[-1].split()]
                    elif key == 'area':
                        data[key] = float(line.split()[-1])
                    elif key == 'site_types':
                        line = file_object.readline()
                        site_types = {}
                        while line.strip():
                            num_sites_of_given_type = int(line.strip().split(' ')[1].replace('(', '').replace(')', ''))
                            site_types[line.strip().split(' ')[0]] = num_sites_of_given_type
                            line = file_object.readline()
                        data[key] = site_types
                    num_matches += 1
            line = file_object.readline()
        return data


def parse_simulation_input(path):
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
            elif 'gas_specs_names' in line:
                data['gas_specs_names'] = line.split()[1:]
                dmatch.remove('gas_specs_names')
            elif 'gas_molar_fracs' in line:
                data['gas_molar_fracs'] = [float(x) for x in line.split()[1:]]
                dmatch.remove('gas_molar_fracs')
            line = file_object.readline()
        return data


def get_data_specnum(path, ignore=0.0):
    with open(f"{path}/specnum_output.txt", "r") as infile:
        header = infile.readline().split()
    full_data = np.loadtxt(f"{path}/specnum_output.txt", skiprows=1)
    index = np.where(full_data[:, 2] == find_nearest(full_data[:, 2], float(full_data[-1, 2] * ignore / 100)))[0][0]
    data = np.delete(full_data, slice(0, index), 0)
    return data, header


def get_step_names(path):
    """ Reads a mechanism_input.dat and returns a list of all the steps"""
    steps_names = []

    with open(f"{path}/mechanism_input.dat", 'r') as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()

        if line.startswith('reversible_step'):
            step_name = line.split()[1]
            steps_names.append(step_name)

    return steps_names


def get_stiffness_scalable_steps(path):
    """ Reads a mechanism_input.dat and returns a list of all the steps that are stiffness scalable"""
    steps_with_stiffness_scalable = []

    with open(f"{path}/mechanism_input.dat", 'r') as file:
        lines = file.readlines()

    inside_block = False
    current_step_name = None
    contains_stiffness_scalable = False

    for line in lines:
        line = line.strip()

        if line.startswith('reversible_step'):
            inside_block = True
            current_step_name = line.split()[1]
            contains_stiffness_scalable = False

        if inside_block:
            if 'stiffness_scalable' in line:
                contains_stiffness_scalable = True
            if line == 'end_reversible_step':
                if contains_stiffness_scalable:
                    steps_with_stiffness_scalable.append(current_step_name)
                inside_block = False

    return steps_with_stiffness_scalable
