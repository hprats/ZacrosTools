from pathlib import Path
from typing import Union, Dict, Any, Optional


def parse_general_output_file(output_file: Union[str, Path]) -> Dict[str, Any]:
    """
    Parses the general_output.txt file and extracts simulation information.

    Parameters
    ----------
    output_file : Union[str, Path]
        Path to the general_output.txt file.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing the extracted information, including:
        - 'version': Version of ZACROS used in the simulation.
        - 'n_sites': Number of lattice sites (int).
        - 'area': Total area of the cell (float).
        - 'site_types': Dictionary of site types and their counts.
        - 'current_time_stopped': Time at the end of the simulation (float).
        - 'final_nevents': Number of events performed at the end of the simulation (int).

    Raises
    ------
    FileNotFoundError
        If the output file does not exist.
    """
    # Ensure the output file exists
    output_file = Path(output_file)
    if not output_file.is_file():
        raise FileNotFoundError(f"Output file '{output_file}' does not exist.")

    # Initialize the data dictionary with None values
    data: Dict[str, Any] = {
        'version': None,
        'n_sites': None,
        'area': None,
        'site_types': None,
        'current_time_stopped': None,
        'final_nevents': None
    }

    with output_file.open('r') as f:
        lines = f.readlines()

    # Extract version from header
    version: Optional[str] = None
    in_header = False
    header_delimiter = '+---------------------------------------------------+'
    for line in lines:
        line = line.strip()
        if line == header_delimiter:
            if not in_header:
                # Start of header
                in_header = True
                continue
            else:
                # End of header
                in_header = False
                break  # Break out of the loop
        elif in_header:
            # Look for the line containing 'ZACROS' and extract the version
            if 'ZACROS' in line.upper():
                parts = line.split()
                for idx, part in enumerate(parts):
                    if part.upper() == 'ZACROS' and idx + 1 < len(parts):
                        version = parts[idx + 1]
                        break
                if version:
                    break  # Version found; exit loop

    data['version'] = version  # version is Optional[str], matching the data dict type

    # Flags to control parsing
    in_lattice_setup = False
    in_site_types = False
    in_simulation_stopped = False

    # Dictionary to store site types
    site_types_dict = {}

    # Known block headers
    known_block_headers = {
        'Compiler information:',
        'Threading/multiprocessing information:',
        'Simulation setup:',
        'Energetics setup:',
        'Mechanism setup:',
        'Preparing simulation:',
        'Commencing simulation:',
        'Simulation stopped:'
    }

    # Iterate over lines to parse required information
    for line in lines:
        line = line.strip()

        # Detect block headers
        if line.startswith('Lattice setup:'):
            in_lattice_setup = True
            in_site_types = False
            continue
        elif line.startswith('Simulation stopped:'):
            in_simulation_stopped = True
            continue
        elif line in known_block_headers:
            # Exiting any current block if a new block header is found
            in_lattice_setup = False
            in_site_types = False
            in_simulation_stopped = False
            continue

        # Parse Lattice setup block
        if in_lattice_setup:
            # Check for end of Lattice setup block
            if line.startswith('Finished reading lattice input.'):
                in_lattice_setup = False
                in_site_types = False
                continue

            # Number of lattice sites
            if line.startswith('Number of lattice sites per cell:'):
                parts = line.split(':', 1)
                if len(parts) >= 2:
                    n_sites_str = parts[1].strip()
                    try:
                        data['n_sites'] = int(n_sites_str)
                    except ValueError:
                        pass  # Unable to parse integer
                continue
            elif line.startswith('Number of lattice sites:'):
                parts = line.split(':', 1)
                if len(parts) >= 2:
                    n_sites_str = parts[1].strip()
                    try:
                        data['n_sites'] = int(n_sites_str)
                    except ValueError:
                        pass  # Unable to parse integer
                continue

            # Surface area
            if line.startswith('Lattice surface area:'):
                parts = line.split(':', 1)
                if len(parts) >= 2:
                    area_str = parts[1].strip()
                    try:
                        data['area'] = float(area_str)
                    except ValueError:
                        pass  # Unable to parse float
                continue
            elif line.startswith('Surface area:'):
                parts = line.split(':', 1)
                if len(parts) >= 2:
                    area_str = parts[1].strip()
                    try:
                        data['area'] = float(area_str)
                    except ValueError:
                        pass  # Unable to parse float
                continue

            # Site type names and counts
            if line.startswith('Site type names and total number of sites of that type:') or \
               line.startswith('Site type names and number of sites of that type:'):
                in_site_types = True
                continue

            if in_site_types:
                if not line:
                    # Empty line, end of site types list
                    in_site_types = False
                    continue
                else:
                    # Parse site type entries
                    if '(' in line and ')' in line:
                        # Format: 'tC (72)'
                        parts = line.split('(')
                        site_type = parts[0].strip()
                        count_str = parts[1].split(')')[0].strip()
                        try:
                            count = int(count_str)
                            site_types_dict[site_type] = count
                        except ValueError:
                            pass  # Unable to parse integer
                        continue
                    else:
                        # Format: 'StTp1 40'
                        parts = line.split()
                        if len(parts) >= 2:
                            site_type = parts[0]
                            count_str = parts[1]
                            try:
                                count = int(count_str)
                                site_types_dict[site_type] = count
                            except ValueError:
                                pass  # Unable to parse integer
                            continue
                        else:
                            # Line does not match expected format
                            in_site_types = False
                            continue

        # Parse Simulation stopped block
        if in_simulation_stopped:
            # Current time stopped
            if line.startswith('Current KMC time:'):
                parts = line.split(':', 1)
                if len(parts) >= 2:
                    time_str = parts[1].strip()
                    try:
                        data['current_time_stopped'] = float(time_str)
                    except ValueError:
                        pass  # Unable to parse float
                continue

            # Final number of events
            if line.startswith('Events occurred:'):
                parts = line.split(':', 1)
                if len(parts) >= 2:
                    events_str = parts[1].strip()
                    try:
                        data['final_nevents'] = int(events_str)
                    except ValueError:
                        pass  # Unable to parse integer
                continue

            # End of Simulation stopped block
            if line == '':
                in_simulation_stopped = False

    # Assign site_types_dict if not empty
    if site_types_dict:
        data['site_types'] = site_types_dict

    # Return the dictionary with extracted information
    return data
