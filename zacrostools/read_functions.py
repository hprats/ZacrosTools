import os
from zacrostools.parse_input_files import parse_simulation_input_file
from zacrostools.custom_exceptions import EnergeticsModelError


def get_partial_pressures(path):
    partial_pressures = {}
    simulation_data = parse_simulation_input_file(input_file=f"{path}/simulation_input.dat")
    for i, molecule in enumerate(simulation_data['gas_specs_names']):
        partial_pressures[molecule] = simulation_data['pressure'] * simulation_data['gas_molar_fracs'][i]
    return partial_pressures


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
    parsed_sim_data = parse_simulation_input_file(input_file=f"{path}/simulation_input.dat")
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



