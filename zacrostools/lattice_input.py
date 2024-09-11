import numpy as np
from zacrostools.write_functions import write_header
from zacrostools.custom_exceptions import LatticeModelError, enforce_types


class LatticeModel:
    """A class that represents a lattice model.

    Parameters
    ----------
    lines: list of str
        Lines that will be printed in the lattice_input.dat.
    """

    @enforce_types
    def __init__(self, lines: list = None, lattice_type: str = None):
        self.lines = lines
        self.lattice_type = lattice_type

    @classmethod
    @enforce_types
    def from_file(cls, filepath: str):
        """Create a LatticeModel by reading an existing lattice_input.dat file.

        Parameters
        ----------
        filepath: str
            Path of the file that will be used as the lattice_input.dat. This file can have any name.


        Returns
        -------
        lattice_model: LatticeModel

        """

        lattice_lines = []
        start_pattern_detected = False
        end_pattern_detected = False

        with open(filepath, 'r') as infile:

            while not start_pattern_detected:
                line = infile.readline()
                if 'default_choice' in line or 'periodic_cell' in line or 'explicit' in line:
                    lattice_lines.append(line)
                    start_pattern_detected = True

            if 'default_choice' in line:
                lattice_type = 'default'
            elif 'periodic_cell' in line:
                lattice_type = 'custom_periodic'
            else:
                lattice_type = 'custom_non_periodic'

            while not end_pattern_detected:
                line = infile.readline()
                if 'end_lattice' in line:
                    lattice_lines.append(line)
                    end_pattern_detected = True
                else:
                    lattice_lines.append(line)

        lattice_model = cls(lines=lattice_lines, lattice_type=lattice_type)
        return lattice_model

    @enforce_types
    def write_lattice_input(self, path: str):
        """Write the lattice_input.dat file.

        Parameters
        ----------
        path: str
            Path to the directory where the lattice_input.dat file will be written.

        """
        write_header(f"{path}/lattice_input.dat")
        with open(f"{path}/lattice_input.dat", 'a') as infile:
            for line in self.lines:
                infile.write(line)

    @enforce_types
    def repeat_cell(self, repeat_cell: list):
        """Modify the value of the repeat_cell keyword in the lattice_input.dat file.

        Parameters
        ----------
        repeat_cell: list of int, optional
            Updates the repeat_cell keyword in lattice_input.dat file.

        """
        if self.lattice_type == 'custom_non_periodic':
            raise LatticeModelError("repeat_cell()' method can not be used with custom non-periodic lattices.")
        i = 0
        line = self.lines[i]
        if self.lattice_type == 'custom_periodic':
            while 'repeat_cell' not in line:
                i += 1
                line = self.lines[i]
            self.lines[i] = f'   repeat_cell {repeat_cell[0]} {repeat_cell[1]}\n'
        else:
            while not any(keyword in line for keyword in
                          ['triangular_periodic', 'rectangular_periodic', 'hexagonal_periodic']):
                i += 1
                line = self.lines[i]
            keyword = line.split()[0]
            lattice_constant = line.split()[1]
            self.lines[i] = f'   {keyword} {lattice_constant} {repeat_cell[0]} {repeat_cell[1]}\n'


def cartesian_to_direct(coords, cell_vectors):
    return tuple(np.linalg.solve(cell_vectors, coords))


def direct_to_cartesian(coords, cell_vectors):
    return tuple(np.dot(cell_vectors, coords))


def distance(coord1, coord2):
    return np.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)


def generate_lattice_model(cell_vectors, sites, coords_type='direct'):

    # Make sure that all numbers in cell_vectors are float (otherwise, Zacros will complain)
    cell_vectors = tuple(tuple(float(num) for num in inner_tuple) for inner_tuple in cell_vectors)

    # Prepare the lattice model dictionary
    lattice_model = {
        'cell_vectors': cell_vectors,  # New cell vectors
        'sites': {}  # Dictionary to store site information
    }

    # Write cartesian and direct coordinates
    site_id = 1
    for site_type, coords in sites.items():

        if coords_type == 'direct':
            cartesian_coords = direct_to_cartesian(coords, cell_vectors)
            lattice_model['sites'][site_id] = {
                'site_type': site_type,
                'cartesian_coords': cartesian_coords,
                'direct_coords': coords}

        elif coords_type == 'cartesian':
            direct_coords = cartesian_to_direct(coords, cell_vectors)
            lattice_model['sites'][site_id] = {
                'site_type': site_type,
                'cartesian_coords': coords,
                'direct_coords': direct_coords}

        else:
            raise LatticeModelError(f"coords_type '{coords_type}' is not allowed, must be 'direct' or 'cartesian'")

        site_id += 1

    return lattice_model


def repeat_lattice_model(lattice_model, num_rep_a, num_rep_b, decimal_places=8):
    """
    Generates a dictionary representing the lattice model including cell vectors, number of sites, and site details.

    Parameters:
    - num_rep_a: Number of repetitions in the direction of vector α.
    - num_rep_b: Number of repetitions in the direction of vector β.
    - decimal_places: Number of decimal places to round the coordinates.

    Returns:
    - lattice_model: Dictionary containing the new cell vectors, number of sites, and site information.
    """

    new_lattice_model = {}

    (a1, a2), (b1, b2) = lattice_model['cell_vectors']
    new_cell_vectors = ((a1 * num_rep_a, a2 * num_rep_a), (b1 * num_rep_b, b2 * num_rep_b))
    new_lattice_model['cell_vectors'] = new_cell_vectors

    new_sites = {}
    site_id = 1
    # Loop over the repetitions of the unit cell in the A and B directions
    for j in range(num_rep_b):
        for i in range(num_rep_a):
            for site in lattice_model['sites']:
                # Compute the cartesian coordinates in the expanded cell
                direct_coords = lattice_model['sites'][site]['direct_coords']
                new_cartesian_x = direct_coords[0] * a1 + direct_coords[1] * b1 + i * a1 + j * b1
                new_cartesian_y = direct_coords[0] * a2 + direct_coords[1] * b2 + i * a2 + j * b2
                new_cartesian_coords = (new_cartesian_x, new_cartesian_y)

                # Round cartesian coordinates to avoid floating-point precision errors
                new_cartesian_coords = tuple(round(coord, decimal_places) for coord in new_cartesian_coords)

                # Convert the rounded cartesian coordinates back to direct
                new_direct_coords = cartesian_to_direct(new_cartesian_coords, new_cell_vectors)

                # Round direct coordinates as well
                new_direct_coords = tuple(round(coord, decimal_places) for coord in new_direct_coords)

                new_sites[site_id] = {
                    'site_type': lattice_model['sites'][site]['site_type'],
                    'cartesian_coords': new_cartesian_coords,
                    'direct_coords': new_direct_coords
                }
                site_id += 1

    new_lattice_model['sites'] = new_sites

    return new_lattice_model


def get_periodic_replicas(lattice_model, direction):
    """Function to generate Cartesian coordinates of periodic replicas"""

    # Determine the direction
    directions = {
        'east': (1, 0),
        'north': (0, 1),
        'northeast': (1, 1),
        'southeast': (1, -1)
    }

    if direction in directions:
        da, db = directions[direction]
    else:
        raise LatticeModelError(
            f"Direction {direction} is not valid. Must be 'east', 'north', 'northeast', or 'southeast'")

    (a1, a2), (b1, b2) = lattice_model['cell_vectors']

    sites_replica = {}
    for site in lattice_model['sites']:
        site_type = lattice_model['sites'][site]['site_type']
        original_coord = lattice_model['sites'][site]['cartesian_coords']
        site_replica_x = original_coord[0] + da * (a1, a2)[0] + db * (b1, b2)[0]
        site_replica_y = original_coord[1] + da * (a1, a2)[1] + db * (b1, b2)[1]
        sites_replica[site] = {'site_type': site_type, 'cartesian_coords': (site_replica_x, site_replica_y)}

    return sites_replica


def create_neighbor_structure(lattice_model, max_distances):
    """
    Creates a neighboring structure for a given lattice model.
    The neighbors list includes directions for connections with periodic replicas.

    Parameters:
    - lattice_model: Dictionary containing lattice details..
    - max_distances: Dictionary specifying the distance thresholds for different site type pairs.

    Returns:
    - neighbors: List of strings representing the neighboring relationships.
    """

    sites = lattice_model['sites']
    site_ids = list(sites.keys())
    neighbors = []

    # Self
    for i in range(len(site_ids)):
        for j in range(i + 1, len(site_ids)):
            site_id1, site_id2 = site_ids[i], site_ids[j]
            site1 = sites[site_id1]
            site2 = sites[site_id2]
            type1, coords1 = site1['site_type'], site1['cartesian_coords']
            type2, coords2 = site2['site_type'], site2['cartesian_coords']
            site_type_pair = f'{min(type1, type2)}-{max(type1, type2)}'
            if site_type_pair in max_distances and distance(coords1, coords2) <= max_distances[site_type_pair]:
                neighbors.append(f"{site_id1}-{site_id2} self")

    # Periodic replicas
    for direction in ['north', 'east', 'northeast', 'southeast']:
        sites_replica = get_periodic_replicas(lattice_model, direction)
        for i in range(len(site_ids)):
            for j in range(len(site_ids)):
                site_id1, site_id2 = site_ids[i], site_ids[j]
                site1 = sites[site_id1]
                site2 = sites_replica[site_id2]
                type1, coords1 = site1['site_type'], site1['cartesian_coords']
                type2, coords2 = site2['site_type'], site2['cartesian_coords']
                site_type_pair = f'{min(type1, type2)}-{max(type1, type2)}'
                if site_type_pair in max_distances and distance(coords1, coords2) <= max_distances[site_type_pair]:
                    neighbors.append(f"{site_id1}-{site_id2} {direction}")

    return neighbors


def remove_sites(lattice_model, site_ids):

    sites = lattice_model['sites']

    # Remove the specified keys from the sites dictionary
    for key in site_ids:
        if key in sites:
            del sites[key]

    # Create a new dictionary with renumbered keys
    new_sites = {}
    new_id = 1
    for old_id in sorted(sites.keys()):
        new_sites[new_id] = sites[old_id]
        new_id += 1

    lattice_model['sites'] = new_sites

    return lattice_model


def add_site(lattice_model, site_type, coords, coords_type):

    sites = lattice_model['sites']

    new_site_id = max(sites.keys()) + 1 if sites else 1  # If sites is empty, start from 1

    # Convert coordinates if needed
    if coords_type == 'direct':
        cartesian_coords = direct_to_cartesian(coords, lattice_model['cell_vectors'])
        direct_coords = coords
    elif coords_type == 'cartesian':
        direct_coords = cartesian_to_direct(coords, lattice_model['cell_vectors'])
        cartesian_coords = coords
    else:
        raise ValueError("coord_type must be 'direct' or 'cartesian'.")

    # Add the new site to the dictionary
    sites[new_site_id] = {
        'site_type': site_type,
        'cartesian_coords': cartesian_coords,
        'direct_coords': direct_coords
    }

    lattice_model['sites'] = sites

    return lattice_model


def write_lattice_input(lattice_model, filepath, repeat_cell, max_distances):

    write_header(filepath)
    with open(filepath, 'a') as f:
        f.write("lattice periodic_cell\n\n")

        (a1, a2), (b1, b2) = lattice_model['cell_vectors']
        f.write(f"   cell_vectors\n")
        f.write(f"   {a1} {a2}\n")
        f.write(f"   {b1} {b2}\n")
        f.write(f"   repeat_cell {repeat_cell[0]} {repeat_cell[1]}\n")
        f.write(f"   n_cell_sites {len(lattice_model['sites'])}\n")
        unique_site_types = {site_info['site_type'] for site_info in lattice_model['sites'].values()}
        n_site_types = len(unique_site_types)
        f.write(f"   n_site_types {n_site_types}\n")
        f.write(f"   site_type_names {' '.join(unique_site_types)}\n")
        site_type_list = [site_info['site_type'] for site_info in lattice_model['sites'].values()]
        f.write(f"   site_types {' '.join(site_type_list)}\n")
        f.write(f"   site_coordinates\n")
        for site in lattice_model['sites']:
            x = lattice_model['sites'][site]['direct_coords'][0]
            y = lattice_model['sites'][site]['direct_coords'][1]
            f.write(f"      {x} {y}\n")
        f.write(f"   neighboring_structure\n")
        neighboring_list = create_neighbor_structure(lattice_model=lattice_model, max_distances=max_distances)
        for link in neighboring_list:
            f.write(f"      {link}\n")
        f.write("   end_neighboring_structure\n\n")
        f.write("end_lattice\n")


