import os
import numpy as np
from zacrostools.custom_exceptions import EnergeticsModelError
from zacrostools.custom_exceptions import KMCOutputError


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
    def process_values(keyword, values):
        if not values:
            # No values, set to True
            return True

        # Define keywords that should always return lists
        list_keywords = {'gas_specs_names', 'gas_energies', 'gas_molec_weights',
                         'gas_molar_fracs', 'surf_specs_names', 'surf_specs_dent'}

        # For surf_specs_names, remove '*'
        if keyword == 'surf_specs_names':
            return [name.rstrip('*') for name in values]

        # For 'override_array_bounds', store value as a string
        if keyword == 'override_array_bounds':
            return ' '.join(values)

        # For stopping_criteria keywords, handle 'infinite' as string
        if keyword in stopping_keywords:
            val = ' '.join(values)
            if val.lower() in ['infinity', 'infinite']:
                return 'infinity'
            else:
                if keyword == 'max_steps':
                    try:
                        return int(val)
                    except ValueError:
                        return val  # Return as string if cannot parse
                else:
                    try:
                        return float(val)
                    except ValueError:
                        return val  # Return as string if cannot parse

        # For reporting_scheme keywords, store values as strings
        if keyword in reporting_keywords:
            return ' '.join(values)

        # For certain keywords, always return a list
        if keyword in list_keywords:
            try:
                return [int(v) for v in values]
            except ValueError:
                try:
                    return [float(v) for v in values]
                except ValueError:
                    return values  # Return as list of strings

        # Default handling
        if len(values) == 1:
            val = values[0]
            try:
                return int(val)
            except ValueError:
                try:
                    return float(val)
                except ValueError:
                    return val  # Return as string
        else:
            # Multiple values, try to parse as list of ints
            try:
                return [int(v) for v in values]
            except ValueError:
                # Try to parse as list of floats
                try:
                    return [float(v) for v in values]
                except ValueError:
                    # Return as list of strings
                    return values

    data = {}
    reporting_scheme = {}
    stopping_criteria = {}
    reporting_keywords = ['snapshots', 'process_statistics', 'species_numbers']
    stopping_keywords = ['max_steps', 'max_time', 'wall_time']

    # Initialize the special keywords with None
    for key in reporting_keywords:
        reporting_scheme[key] = None
    for key in stopping_keywords:
        stopping_criteria[key] = None

    filename = os.path.join(path, 'simulation_input.dat')
    with open(filename, 'r') as f:
        lines = f.readlines()
    current_keyword = None
    current_values = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line == 'finish':
            continue
        # Check if line starts with a keyword
        if not line[0].isspace():
            # New keyword line
            tokens = line.split()
            keyword = tokens[0]
            values = tokens[1:]
            # If we were collecting values for a previous keyword, store them
            if current_keyword is not None:
                if current_keyword in reporting_keywords:
                    reporting_scheme[current_keyword] = process_values(current_keyword, current_values)
                elif current_keyword in stopping_keywords:
                    stopping_criteria[current_keyword] = process_values(current_keyword, current_values)
                else:
                    data[current_keyword] = process_values(current_keyword, current_values)
            # Start collecting values for the new keyword
            current_keyword = keyword
            current_values = values
        else:
            # Continuation line, add tokens to current_values
            tokens = line.split()
            current_values.extend(tokens)
    # After processing all lines, store the last keyword's values
    if current_keyword is not None:
        if current_keyword in reporting_keywords:
            reporting_scheme[current_keyword] = process_values(current_keyword, current_values)
        elif current_keyword in stopping_keywords:
            stopping_criteria[current_keyword] = process_values(current_keyword, current_values)
        else:
            data[current_keyword] = process_values(current_keyword, current_values)
    # Add reporting_scheme and stopping_criteria to data
    data['reporting_scheme'] = reporting_scheme
    data['stopping_criteria'] = stopping_criteria
    return data



def get_partial_pressures(path):
    partial_pressures = {}
    simulation_data = parse_simulation_input(path)
    for i, molecule in enumerate(simulation_data['gas_specs_names']):
        partial_pressures[molecule] = simulation_data['pressure'] * simulation_data['gas_molar_fracs'][i]
    return partial_pressures


def get_data_specnum(path, window_percent, window_type):
    if window_type == 'time':
        column_index = 2
    elif window_type == 'nevents':
        column_index = 1
    else:
        raise KMCOutputError("'window_type' must be either 'time' or 'nevents'")

    with open(f"{path}/specnum_output.txt", "r") as infile:
        header = infile.readline().split()
    data = np.loadtxt(f"{path}/specnum_output.txt", skiprows=1)
    column = data[:, column_index]
    final_value = column[-1]
    value_initial_percent = window_percent[0] / 100.0 * final_value
    value_final_percent = window_percent[1] / 100.0 * final_value
    data_slice = data[(column >= value_initial_percent) & (column <= value_final_percent)]
    return data_slice, header


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


def get_surf_specs_data(path):

    # Get data from simulation_input.dat
    parsed_sim_data = parse_simulation_input(path)
    surf_specs_names = parsed_sim_data.get('surf_specs_names')
    surf_specs_dent = parsed_sim_data.get('surf_specs_dent')
    species_dentates = dict(zip(surf_specs_names, surf_specs_dent))
    species_in_simulation = set(surf_specs_names)

    surf_specs_data = {}

    # Check if the user is using a default lattice or not
    default_lattice = check_default_lattice(path)

    if default_lattice:
        for species in surf_specs_names:
            surf_specs_data[species] = {
                'surf_specs_dent': species_dentates[species],
                'site_type': 'StTp1'
            }

    else:

        with open(os.path.join(path, 'energetics_input.dat'), 'r') as f:
            lines = f.readlines()

        species_site_types = {}
        num_lines = len(lines)
        i = 0
        while i < num_lines:
            line = lines[i].strip()
            if line.startswith('cluster'):
                cluster_species = []
                site_types = []
                i += 1
                while i < num_lines:
                    line = lines[i].strip()
                    if line.startswith('end_cluster'):
                        break
                    elif line.startswith('lattice_state'):
                        # Process lattice_state block
                        i += 1  # Move to the next line after 'lattice_state'
                        while i < num_lines:
                            line = lines[i].strip()
                            if not line or line.startswith('#'):
                                i += 1
                                continue
                            if line.startswith('site_types') or line.startswith('cluster_eng') or line.startswith(
                                    'neighboring') or line.startswith('end_cluster'):
                                break  # End of lattice_state block
                            tokens = line.split()
                            if tokens and tokens[0].isdigit():
                                species_name = tokens[1].rstrip('*')
                                cluster_species.append(species_name)
                            i += 1
                    elif line.startswith('site_types'):
                        tokens = line.split()
                        site_types = tokens[1:]
                        i += 1  # Move to the next line after 'site_types'
                        continue  # Continue to process other lines in the cluster
                    else:
                        i += 1
                # After processing the cluster
                if len(cluster_species) != len(site_types):
                    raise EnergeticsModelError(f"Mismatch between number of species and site_types in a cluster in line {i+1}."
                                              f"\nCluster species: {cluster_species}"
                                              f"\nSite types: {site_types}")
                # Associate species with site types
                for species, site_type in zip(cluster_species, site_types):
                    if species not in species_in_simulation:
                        raise EnergeticsModelError(
                            f"Species '{species}' declared in energetics_input.dat but not in surf_specs_names.")
                    if species in species_site_types:
                        if species_site_types[species] != site_type:
                            raise EnergeticsModelError(
                                f"Species '{species}' is adsorbed on multiple site types: '{species_site_types[species]}' and '{site_type}'")
                    else:
                        species_site_types[species] = site_type
                i += 1  # Move past 'end_cluster'
            else:
                i += 1

        for species in surf_specs_names:
            if species not in species_site_types:
                raise EnergeticsModelError(f"Species '{species}' declared in surf_specs_names but not found in energetics_input.dat.")
            surf_specs_data[species] = {
                'surf_specs_dent': species_dentates[species],
                'site_type': species_site_types[species]
            }
    return surf_specs_data


def check_default_lattice(path):
    with open(os.path.join(path, 'lattice_input.dat'), 'r') as file:
        for line in file:
            # Check if both 'lattice' and 'default_choice' are in the same line
            if 'lattice' in line and 'default_choice' in line:
                return True

    return False



