from pathlib import Path
from typing import Union, Dict, Any
from zacrostools.custom_exceptions import LatticeModelError


def parse_simulation_input_file(input_file: Union[str, Path]) -> Dict[str, Any]:
    """
    Parses a simulation_input.dat file and extracts the simulation parameters.

    Parameters
    ----------
    input_file : Union[str, Path]
        Path to the simulation input file.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing the extracted parameters, including:
        - General simulation parameters as key-value pairs.
        - Nested dictionaries for 'reporting_scheme' and 'stopping_criteria' containing specific parameters.

    Raises
    ------
    FileNotFoundError
        If the input file does not exist.
    ValueError
        If specific parameters have invalid formats or cannot be parsed.
    """

    def process_values(kword, vals):
        if not vals:
            # No values, set to True
            return True

        # Define keywords that should always return lists
        list_keywords = {'gas_specs_names', 'gas_energies', 'gas_molec_weights',
                         'gas_molar_fracs', 'surf_specs_names', 'surf_specs_dent'}

        # For surf_specs_names, remove '*'
        if kword == 'surf_specs_names':
            return [name.rstrip('*') for name in vals]

        # For 'override_array_bounds', store value as a string
        if kword == 'override_array_bounds':
            return ' '.join(vals)

        # For stopping_criteria keywords, handle 'infinite' as string
        if kword in stopping_keywords:
            val = ' '.join(vals)
            if val.lower() in ['infinity', 'infinite']:
                return 'infinity'
            else:
                if kword == 'max_steps':
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
        if kword in reporting_keywords:
            return ' '.join(vals)

        # For certain keywords, always return a list
        if kword in list_keywords:
            try:
                return [int(v) for v in vals]
            except ValueError:
                try:
                    return [float(v) for v in vals]
                except ValueError:
                    return vals  # Return as list of strings

        # Default handling
        if len(vals) == 1:
            val = vals[0]
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
                return [int(v) for v in vals]
            except ValueError:
                # Try to parse as list of floats
                try:
                    return [float(v) for v in vals]
                except ValueError:
                    # Return as list of strings
                    return vals

    input_file = Path(input_file)
    if not input_file.is_file():
        raise FileNotFoundError(f"Input file '{input_file}' does not exist.")

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

    with input_file.open('r') as f:
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


def parse_lattice_input_file(input_file: Union[str, Path]) -> Dict[str, Any]:
    """
    Parses a lattice_input.dat file and extracts the lattice parameters.

    Parameters
    ----------
    input_file : Union[str, Path]
        Path to the lattice input file.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing the extracted parameters, including:
        - lattice_type
        - default_lattice_type
        - lattice_constant
        - copies
        - cell_vectors
        - sites
        - coordinate_type
        - neighboring_structure

    Raises
    ------
    LatticeModelError
        If the file cannot be read, the lattice block is missing, or if required parameters are invalid or missing.
    """
    # Ensure the input file exists
    input_file = Path(input_file)
    if not input_file.is_file():
        raise LatticeModelError(f"Input file '{input_file}' does not exist.")

    # Read all lines from the input file
    with input_file.open('r') as f:
        lines = f.readlines()

    # Initialize variables to identify the lattice block
    lattice_block = []      # List to store lines within the lattice block
    inside_lattice_block = False
    lattice_type = None

    # Iterate through each line to find the lattice block
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith('lattice'):  # Start of the lattice block
            inside_lattice_block = True
            parts = stripped_line.split()  # The first line should be 'lattice lattice_type'
            if len(parts) < 2:
                raise LatticeModelError("Invalid lattice block: missing lattice type.")
            lattice_type = parts[1]
            lattice_block.append(line)
        elif stripped_line.startswith('end_lattice'):  # End of the lattice block
            lattice_block.append(line)
            break  # Stop reading further lines
        elif inside_lattice_block:  # Lines within the lattice block
            lattice_block.append(line)

    # Check if the lattice block was found
    if not lattice_block:
        raise LatticeModelError("No lattice block found in the input file.")

    # Prepare a dictionary to store parsed data
    parsed_data = {'lattice_type': lattice_type}

    # Parse parameters based on the lattice_type
    if lattice_type == 'default_choice':
        # Handle 'default_choice' lattice type
        params_line = None
        # Find the line containing the parameters
        for line in lattice_block[1:]:
            stripped_line = line.strip()
            if stripped_line == '' or stripped_line.startswith('#'):
                continue  # Skip empty lines and comments
            params_line = stripped_line
            break  # Parameters found

        if params_line is None:
            raise LatticeModelError("No parameters found for 'default_choice' lattice.")

        # Extract parameters
        parts = params_line.split()
        if len(parts) != 4:
            raise LatticeModelError("Invalid parameters for 'default_choice' lattice. Expected 4 parameters.")

        default_lattice_type, lattice_constant_str, copies0_str, copies1_str = parts
        parsed_data['default_lattice_type'] = default_lattice_type
        parsed_data['lattice_constant'] = float(lattice_constant_str)
        parsed_data['copies'] = [int(copies0_str), int(copies1_str)]

    elif lattice_type == 'periodic_cell':
        # Handle 'periodic_cell' lattice type

        # Initialize variables to store lattice parameters
        cell_vectors = []
        copies = None
        coordinate_type = 'direct'  # Default coordinate type
        n_cell_sites = None
        site_type_names = []
        site_types = []
        site_coordinates = []
        neighboring_structure = {}
        in_cell_vectors = False
        in_site_coordinates = False
        in_neighboring_structure = False

        # Iterate through the lattice block to extract parameters
        for line in lattice_block[1:]:
            stripped_line = line.strip()
            if stripped_line == '' or stripped_line.startswith('#'):
                continue  # Skip empty lines and comments

            if stripped_line.startswith('cell_vectors'):
                # Start reading cell vectors
                in_cell_vectors = True
                continue
            elif stripped_line.startswith('repeat_cell'):
                # Extract repeat_cell values (copies)
                parts = stripped_line.split()
                copies = [int(parts[1]), int(parts[2])]
            elif stripped_line.startswith('coordinate_type'):
                # Extract coordinate type
                parts = stripped_line.split()
                coordinate_type = parts[1]
            elif stripped_line.startswith('n_cell_sites'):
                # Extract number of cell sites
                n_cell_sites = int(stripped_line.split()[1])
            elif stripped_line.startswith('n_site_types'):
                # Number of site types (not used in this function)
                pass  # No action needed
            elif stripped_line.startswith('site_type_names'):
                # Extract site type names
                parts = stripped_line.split()
                site_type_names = parts[1:]
            elif stripped_line.startswith('site_types'):
                # Extract site types for each site
                parts = stripped_line.split()
                site_types = parts[1:]
            elif stripped_line.startswith('site_coordinates'):
                # Start reading site coordinates
                in_site_coordinates = True
                continue
            elif stripped_line.startswith('neighboring_structure'):
                # Start reading neighboring structure
                in_neighboring_structure = True
                continue
            elif stripped_line.startswith('end_neighboring_structure'):
                # End of neighboring structure section
                in_neighboring_structure = False
                continue
            elif stripped_line.startswith('end_lattice'):
                # End of lattice block
                break
            elif in_cell_vectors:
                # Read cell vector components
                vec_parts = stripped_line.split()
                if len(vec_parts) != 2:
                    raise LatticeModelError("Invalid cell vector format.")
                cell_vectors.append((float(vec_parts[0]), float(vec_parts[1])))
                if len(cell_vectors) == 2:
                    in_cell_vectors = False  # All cell vectors read
            elif in_site_coordinates:
                # Read site coordinates
                coord_parts = stripped_line.split()
                if len(coord_parts) != 2:
                    raise LatticeModelError("Invalid site coordinate format.")
                site_coordinates.append((float(coord_parts[0]), float(coord_parts[1])))
                if len(site_coordinates) == n_cell_sites:
                    in_site_coordinates = False  # All site coordinates read
            elif in_neighboring_structure:
                # Read neighboring structure entries
                parts = stripped_line.split()
                if len(parts) != 2:
                    raise LatticeModelError("Invalid neighboring structure entry.")
                pair = parts[0]
                keyword = parts[1]
                if pair in neighboring_structure:
                    if keyword not in neighboring_structure[pair]:
                        neighboring_structure[pair].append(keyword)
                else:
                    neighboring_structure[pair] = [keyword]
            else:
                # Unhandled line or comments; no action needed
                continue

        # Validate that necessary site information has been read
        if not site_type_names or not site_types or not site_coordinates:
            raise LatticeModelError("Missing site information in the lattice file.")

        # Check that the number of site types matches the number of site coordinates
        if len(site_types) != len(site_coordinates):
            raise LatticeModelError("Mismatch between number of site types and site coordinates.")

        # Construct the 'sites' dictionary mapping site types to coordinates
        sites = {}
        for stype, coord in zip(site_types, site_coordinates):
            if stype not in sites:
                sites[stype] = []
            sites[stype].append(coord)

        # Store the parsed parameters in the dictionary
        parsed_data['cell_vectors'] = tuple(cell_vectors)
        parsed_data['copies'] = copies
        parsed_data['coordinate_type'] = coordinate_type
        parsed_data['sites'] = sites
        parsed_data['neighboring_structure'] = neighboring_structure

    elif lattice_type == 'explicit':
        # Explicit lattice type is not supported
        raise LatticeModelError("The 'explicit' lattice_type is not yet supported.")

    else:
        # Unsupported lattice type encountered
        raise LatticeModelError(f"Unsupported lattice_type '{lattice_type}'.")

    # Return the dictionary containing all parsed parameters
    return parsed_data
