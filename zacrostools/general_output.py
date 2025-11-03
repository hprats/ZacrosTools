import numpy as np
import pandas as pd
from pathlib import Path
from typing import Union, Dict, Any, List, Optional


def parse_general_output_file(
        output_file: Union[str, Path],
        parse_stiffness_coefficients: bool = False
) -> Dict[str, Any]:
    """
    Parses the general_output.txt file from a Zacros simulation and extracts
    various simulation parameters.

    Parameters
    ----------
    output_file : Union[str, Path]
        Path to the general_output.txt file.
    parse_stiffness_coefficients : bool, optional
        If True, parse stiffness coefficients from the Commencing simulation block.
        Default is False.

    Returns
    -------
    data : Dict[str, Any]
        A dictionary containing parsed information including:
            'version': str
            From Simulation setup:
                'random_seed': int
                'temperature': float
                'pressure': float
                'n_gas_species': int
                'gas_specs_names': List[str]
                'gas_energies': List[float]
                'gas_molar_fracs': List[float]
                'n_surf_species': int
                'surf_specs_names': List[str]
                'surf_specs_dent': List[int]
                'enable_stiffness_scaling': bool
                'stiffness_scaling_algorithm': Optional[str]  # 'prats2024', 'legacy', or None
                'stiffness_scaling_tags': Optional[Dict[str, Union[int, float]]]
            From Lattice setup:
                'area': float
                'n_sites': int
                'n_site_types': int
                'site_types': Dict[str, int]
            From Mechanism setup:
                'n_steps': int
                # If enable_stiffness_scaling=True and algorithm='legacy':
                #   'stiffness_scalable_steps': List[str]
                # If enable_stiffness_scaling=True and algorithm='prats2024':
                #   'non_symmetric_stiffness_scalable_steps': List[str]
                #   'symmetric_stiffness_scalable_steps': List[str]
                #   'stiffness_scalable_steps': List[str]
    """


    output_file = Path(output_file)
    with output_file.open('r') as f:
        lines = f.readlines()

    data: Dict[str, Any] = {}

    # Define known blocks for reference
    known_blocks = [
        "Compiler information:",
        "Threading/multiprocessing information:",
        "Simulation setup:",
        "Lattice setup:",
        "Energetics setup:",
        "Mechanism setup:",
        "Initial state setup:",
        "Preparing simulation:",
        "Commencing simulation:",
        "Simulation stopped:",
        "Performance facts:",
        "Execution queue statistics:",
        "Memory usage statistics:"
    ]

    # Helper function to find block lines
    def find_block(full_lines: List[str], block_name: str, blocks: List[str]):
        start = None
        end = None
        for i, line in enumerate(full_lines):
            if line.strip() == block_name:
                start = i
            elif start is not None and line.strip() in blocks and line.strip() != block_name:
                end = i
                break
        if start is not None and end is None:
            end = len(full_lines)
        return start, end

    # Parsing functions
    def parse_header(full_lines: List[str]) -> str:
        """
        Parse the header of the file to extract the version.
        """
        version = None
        for line in full_lines:
            if "ZACROS" in line:
                parts = line.strip("|").strip().split()
                if "ZACROS" in parts:
                    idx = parts.index("ZACROS")
                    if idx + 1 < len(parts):
                        version = parts[idx + 1]
                        break
        return version

    def parse_compiler_information(full_lines: List[str], blocks: List[str]):
        start, end = find_block(full_lines, "Compiler information:", blocks)
        # For now, do nothing

    def parse_threading_information(full_lines: List[str], blocks: List[str]):
        start, end = find_block(full_lines, "Threading/multiprocessing information:", blocks)
        # For now, do nothing

    def parse_simulation_setup(full_lines: List[str], blocks: List[str]) -> Dict[str, Any]:
        start, end = find_block(full_lines, "Simulation setup:", blocks)

        data_block: Dict[str, Any] = {
            'random_seed': None,
            'temperature': None,
            'pressure': None,
            'n_gas_species': None,
            'gas_specs_names': None,
            'gas_energies': None,
            'gas_molar_fracs': None,
            'n_surf_species': None,
            'surf_specs_names': None,
            'surf_specs_dent': None,
            'enable_stiffness_scaling': False,
            'stiffness_scaling_algorithm': None,
            'stiffness_scaling_tags': None  # Initialize as None
        }

        if start is not None and end is not None:
            for line in full_lines[start:end]:
                line_stripped = line.strip()
                if not line_stripped:
                    continue

                if line_stripped.startswith("Random sequence with seed:"):
                    parts = line_stripped.split(":")
                    if len(parts) == 2:
                        data_block['random_seed'] = int(parts[1].strip())

                elif line_stripped.startswith("Temperature:"):
                    parts = line_stripped.split(":")
                    if len(parts) == 2:
                        data_block['temperature'] = float(parts[1].strip())

                elif line_stripped.startswith("Pressure:"):
                    parts = line_stripped.split(":")
                    if len(parts) == 2:
                        data_block['pressure'] = float(parts[1].strip())

                elif line_stripped.startswith("Number of gas species:"):
                    parts = line_stripped.split(":")
                    if len(parts) == 2:
                        data_block['n_gas_species'] = int(parts[1].strip())

                elif line_stripped.startswith("Gas species names:"):
                    parts = line_stripped.split(":", 1)
                    if len(parts) == 2:
                        data_block['gas_specs_names'] = parts[1].split()

                elif line_stripped.startswith("Gas species energies:"):
                    parts = line_stripped.split(":", 1)
                    if len(parts) == 2:
                        data_block['gas_energies'] = [float(x) for x in parts[1].split()]

                elif line_stripped.startswith("Gas species molar fractions:"):
                    parts = line_stripped.split(":", 1)
                    if len(parts) == 2:
                        data_block['gas_molar_fracs'] = [float(x) for x in parts[1].split()]

                elif line_stripped.startswith("Number of surface species:"):
                    parts = line_stripped.split(":")
                    if len(parts) == 2:
                        data_block['n_surf_species'] = int(parts[1].strip())

                elif line_stripped.startswith("Surface species names:"):
                    parts = line_stripped.split(":", 1)
                    if len(parts) == 2:
                        surf_names = parts[1].split()
                        data_block['surf_specs_names'] = surf_names

                elif line_stripped.startswith("Surface species dentation:"):
                    parts = line_stripped.split(":", 1)
                    if len(parts) == 2:
                        data_block['surf_specs_dent'] = [int(x) for x in parts[1].split()]

                elif line_stripped.startswith("Keyword enable_stiffness_scaling (prats2024) parsed."):
                    data_block['enable_stiffness_scaling'] = True
                    data_block['stiffness_scaling_algorithm'] = 'prats2024'

                elif line_stripped.startswith("Keyword enable_stiffness_scaling (legacy) parsed."):
                    data_block['enable_stiffness_scaling'] = True
                    data_block['stiffness_scaling_algorithm'] = 'legacy'

                # Parse Stiffness Scaling Tags
                if data_block['enable_stiffness_scaling']:
                    # Initialize the tags dictionary
                    if data_block['stiffness_scaling_tags'] is None:
                        data_block['stiffness_scaling_tags'] = {}

                    # Define mapping based on the algorithm
                    if data_block['stiffness_scaling_algorithm'] == 'prats2024':
                        if line_stripped.startswith("[Stiffness scaling] Frequency of stiffness checks:"):
                            value = line_stripped.split(":", 1)[1].strip()
                            data_block['stiffness_scaling_tags']['check_every'] = int(value)

                        elif line_stripped.startswith(
                                "[Stiffness scaling] Minimum allowed separation of time-scales between fastest non-quasi-equilibrated step and slowest quasi-equilibrated one:"):
                            value = line_stripped.split(":", 1)[1].strip()
                            data_block['stiffness_scaling_tags']['min_separation'] = float(value)

                        elif line_stripped.startswith(
                                "[Stiffness scaling] Maximum allowed separation of time-scales between fastest non-quasi-equilibrated step and slowest quasi-equilibrated one:"):
                            value = line_stripped.split(":", 1)[1].strip()
                            data_block['stiffness_scaling_tags']['max_separation'] = float(value)

                        elif line_stripped.startswith(
                                "[Stiffness scaling] Tolerance on partial-equilibrium ratio for detecting quasi-equilibrated steps:"):
                            value = line_stripped.split(":", 1)[1].strip()
                            data_block['stiffness_scaling_tags']['tol_part_equil_ratio'] = float(value)

                        elif line_stripped.startswith("[Stiffness scaling] Upscaling_factor is set as:"):
                            value = line_stripped.split(":", 1)[1].strip()
                            data_block['stiffness_scaling_tags']['upscaling_factor'] = float(value)

                        elif line_stripped.startswith("[Stiffness scaling] Upscaling_limit is set as:"):
                            value = line_stripped.split(":", 1)[1].strip()
                            data_block['stiffness_scaling_tags']['upscaling_limit'] = float(value)

                        elif line_stripped.startswith("[Stiffness scaling] Downscaling_limit is set as:"):
                            value = line_stripped.split(":", 1)[1].strip()
                            data_block['stiffness_scaling_tags']['downscaling_limit'] = float(value)

                        elif line_stripped.startswith("[Stiffness scaling] min_noccur enevnts:"):
                            value = line_stripped.split(":", 1)[1].strip()
                            data_block['stiffness_scaling_tags']['min_noccur'] = int(value)

                    elif data_block['stiffness_scaling_algorithm'] == 'legacy':
                        if line_stripped.startswith("[Stiffness scaling] Frequency of stiffness checks:"):
                            value = line_stripped.split(":", 1)[1].strip()
                            data_block['stiffness_scaling_tags']['check_every'] = int(value)

                        elif line_stripped.startswith(
                                "[Stiffness scaling] Minimum allowed separation of time-scales between fastest non-quasi-equilibrated step and slowest quasi-equilibrated one:"):
                            value = line_stripped.split(":", 1)[1].strip()
                            data_block['stiffness_scaling_tags']['min_separation'] = float(value)

                        elif line_stripped.startswith(
                                "[Stiffness scaling] Maximum allowed separation of time-scales between fastest non-quasi-equilibrated step and slowest quasi-equilibrated one:"):
                            value = line_stripped.split(":", 1)[1].strip()
                            data_block['stiffness_scaling_tags']['max_separation'] = float(value)

                        elif line_stripped.startswith(
                                "[Stiffness scaling] Tolerance on partial-equilibrium ratio for detecting quasi-equilibrated steps:"):
                            value = line_stripped.split(":", 1)[1].strip()
                            data_block['stiffness_scaling_tags']['tol_part_equil_ratio'] = float(value)

                        elif line_stripped.startswith(
                                "[Stiffness scaling] Threshold on stiffness coefficient for applying scaling:"):
                            value = line_stripped.split(":", 1)[1].strip()
                            data_block['stiffness_scaling_tags']['stiffn_coeff_threshold'] = float(value)

                        elif line_stripped.startswith(
                                "[Stiffness scaling] Factor for scaling up/down the rate constants:"):
                            value = line_stripped.split(":", 1)[1].strip()
                            data_block['stiffness_scaling_tags']['scaling_factor'] = float(value)

                        elif line_stripped.startswith(
                                "[Stiffness scaling] Default maximum allowed separation of time-scales between fastest and slowest quasi-equilibrated steps:"):
                            value = line_stripped.split(":", 1)[1].strip()
                            data_block['stiffness_scaling_tags']['max_qequil_separation'] = float(value)

        return data_block

    def parse_lattice_setup(full_lines: List[str], blocks: List[str], version_str: str) -> Dict[str, Any]:
        """
        Parse the "Lattice setup:" block.

        We need to extract:
            'area' (float)
            'n_sites' (int)
            'n_site_types' (int)
            'site_types' (dict: name->count)
        """
        start, end = find_block(full_lines, "Lattice setup:", blocks)
        data_block: Dict[str, Any] = {
            'area': None,
            'n_sites': None,
            'n_site_types': None,
            'site_types': {}
        }

        if version_str is not None:
            version_val = float(version_str)
        else:
            version_val = 5.0  # default assumption if not found

        # Identify which lines to look for based on version
        if version_val < 3.0:
            area_key = "Surface area:"
            n_sites_key = "Number of lattice sites:"
            site_type_header = "Site type names and number of sites of that type:"
        else:
            area_key = "Lattice surface area:"
            n_sites_key = "Total number of lattice sites:"
            site_type_header = "Site type names and total number of sites of that type:"

        if start is not None and end is not None:
            read_site_types = False
            for line in full_lines[start:end]:
                line_stripped = line.strip()
                if not line_stripped:
                    continue

                if line_stripped.startswith(area_key):
                    parts = line_stripped.split(":", 1)
                    if len(parts) == 2:
                        data_block['area'] = float(parts[1].strip())

                elif line_stripped.startswith(n_sites_key):
                    parts = line_stripped.split(":", 1)
                    if len(parts) == 2:
                        data_block['n_sites'] = int(parts[1].strip())

                elif line_stripped.startswith("Number of site types:"):
                    parts = line_stripped.split(":", 1)
                    if len(parts) == 2:
                        data_block['n_site_types'] = int(parts[1].strip())

                elif line_stripped.startswith(site_type_header):
                    read_site_types = True
                    continue

                elif read_site_types:
                    if line_stripped.startswith("Finished reading lattice input.") or \
                            line_stripped.startswith("Maximum coordination number:"):
                        read_site_types = False
                    else:
                        # Parse lines like: tC (100)
                        if '(' in line_stripped and ')' in line_stripped:
                            name_part, num_part = line_stripped.split('(')
                            name_part = name_part.strip()
                            num_part = num_part.strip(' )')
                            data_block['site_types'][name_part] = int(num_part)

        return data_block

    def parse_energetics_setup(full_lines: List[str], blocks: List[str]):
        start, end = find_block(full_lines, "Energetics setup:", blocks)
        # For now, ignore this block

    def parse_mechanism_setup(full_lines: List[str], blocks: List[str], enable_stiffness: bool,
                              algorithm: Optional[str]) -> Dict[str, Any]:
        """
        Parse the "Mechanism setup:" block.

        Extract:
            'n_steps': int
            If enable_stiffness_scaling == True:
                If algorithm == 'legacy':
                    'stiffness_scalable_steps': List[str]
                If algorithm == 'prats2024':
                    'non_symmetric_stiffness_scalable_steps': List[str]
                    'symmetric_stiffness_scalable_steps': List[str]
                    'stiffness_scalable_steps': List[str]
        """
        start, end = find_block(full_lines, "Mechanism setup:", blocks)

        data_block: Dict[str, Any] = {
            'n_steps': None
        }

        # Initialize variables for stiffness scaling
        data_block['stiffness_scalable_steps'] = None
        data_block['non_symmetric_stiffness_scalable_steps'] = None
        data_block['symmetric_stiffness_scalable_steps'] = None

        if start is not None and end is not None:
            read_legacy_stiff = False
            read_non_symmetric = False
            read_symmetric = False

            legacy_steps = []
            non_sym_steps = []
            sym_steps = []

            for line in full_lines[start:end]:
                line_stripped = line.strip()
                if not line_stripped:
                    continue

                if line_stripped.startswith("Number of elementary steps:"):
                    parts = line_stripped.split(":", 1)
                    if len(parts) == 2:
                        data_block['n_steps'] = int(parts[1].strip())

                if enable_stiffness and algorithm == 'legacy':
                    # Stiffness scaling enabled for the following elementary steps:
                    if line_stripped.startswith("Stiffness scaling enabled for the following elementary steps:"):
                        read_legacy_stiff = True
                        continue
                    elif read_legacy_stiff:
                        # Lines like: "Fwd/Rev: 1/2 - aO2_HfC_fwd/aO2_HfC_rev"
                        if line_stripped.startswith("Fwd/Rev:"):
                            # Extract the base step name
                            parts = line_stripped.split('-', 1)
                            if len(parts) == 2:
                                steps_part = parts[1].strip()
                                fwd_rev = steps_part.split('/')
                                base_name = fwd_rev[0].replace('_fwd', '').replace('_rev', '')
                                legacy_steps.append(base_name)
                        else:
                            # If we hit something else, we might have finished reading
                            # but let's rely on break conditions if needed.
                            pass

                if enable_stiffness and algorithm == 'prats2024':
                    # Stiffness scaling (non-symmetric) enabled...
                    if line_stripped.startswith(
                            "Stiffness scaling (non-symmetric) enabled for the following elementary steps:"):
                        read_non_symmetric = True
                        read_symmetric = False
                        continue
                    elif line_stripped.startswith(
                            "Stiffness scaling (symmetric) enabled for the following elementary steps:"):
                        read_non_symmetric = False
                        read_symmetric = True
                        continue
                    elif read_non_symmetric:
                        # read lines like Fwd/Rev: 1/2 - aO2_HfC_fwd/aO2_HfC_rev
                        if line_stripped.startswith("Fwd/Rev:"):
                            parts = line_stripped.split('-', 1)
                            if len(parts) == 2:
                                steps_part = parts[1].strip()
                                fwd_rev = steps_part.split('/')
                                base_name = fwd_rev[0].replace('_fwd', '').replace('_rev', '')
                                non_sym_steps.append(base_name)
                    elif read_symmetric:
                        if line_stripped.startswith("Fwd/Rev:"):
                            parts = line_stripped.split('-', 1)
                            if len(parts) == 2:
                                steps_part = parts[1].strip()
                                fwd_rev = steps_part.split('/')
                                base_name = fwd_rev[0].replace('_fwd', '').replace('_rev', '')
                                sym_steps.append(base_name)

            # After reading the block, store the lists if needed
            if enable_stiffness and algorithm == 'legacy':
                data_block['stiffness_scalable_steps'] = legacy_steps
            elif enable_stiffness and algorithm == 'prats2024':
                data_block['non_symmetric_stiffness_scalable_steps'] = non_sym_steps
                data_block['symmetric_stiffness_scalable_steps'] = sym_steps
                data_block['stiffness_scalable_steps'] = non_sym_steps + sym_steps

        return data_block

    def parse_preparing_simulation(full_lines: List[str], blocks: List[str]):
        start, end = find_block(full_lines, "Preparing simulation:", blocks)
        # For now, do nothing

    def parse_commencing_simulation(
            full_lines: List[str],
            blocks: List[str],
            parse_stiffness_coefficients: bool,
            stiffness_scalable_steps: List[str],
            algorithm: Union[str, None]
    ) -> Dict[str, Any]:
        """
        Parses the "Commencing simulation:" block.

        Parameters
        ----------
        full_lines : List[str]
            All lines from the output file.
        blocks : List[str]
            List of known block headers to identify the end of the current block.
        parse_stiffness_coefficients : bool
            Flag to determine whether to parse stiffness scaling coefficients.
        stiffness_scalable_steps : List[str]
            List of step names that are stiffness scalable.
        algorithm : Union[str, None]
            The stiffness scaling algorithm used ('prats2024', 'legacy', or None).

        Returns
        -------
        Dict[str, Any]
            A dictionary with the key 'stiffness_scaling_coefficients' containing a Pandas DataFrame
            or None if parsing is not required.
        """

        if not parse_stiffness_coefficients:
            return {'stiffness_scaling_coefficients': None}

        start, end = find_block(full_lines, "Commencing simulation:", blocks)

        if start is None:
            # Block not found
            return {'stiffness_scaling_coefficients': None}

        # Extract the lines within the "Commencing simulation:" block
        block_lines = full_lines[start:end]

        data_dict = {
            'nevents': [0],
            'time': [0.0]
        }

        for step in stiffness_scalable_steps:
            data_dict[step] = [1.0]

        def parse_prats2024(block_lines: List[str], steps: List[str], data_dict: Dict[str, List[Any]]):
            """
            Parses sub-blocks specific to the 'prats2024' algorithm and updates data_dict.

            Parameters
            ----------
            block_lines : List[str]
                Lines within the "Commencing simulation:" block.
            steps : List[str]
                List of stiffness scalable steps.
            data_dict : Dict[str, List[Any]]
                Dictionary to store parsed data.
            """
            i = 0
            n = len(block_lines)

            # Skip the initial settings sub-block
            while i < n:
                line = block_lines[i].strip()
                if line.startswith("Stiffness scaling module invoked at time t = "):
                    break
                i += 1

            # Iterate through the remaining lines to parse each invocation sub-block
            while i < n:
                line = block_lines[i].strip()

                if line.startswith("Stiffness scaling module invoked at time t = "):
                    # Example line:
                    # "Stiffness scaling module invoked at time t = 1.2609349242516475E-006 and number of steps = 16000:"

                    # Extract the portion after the prefix
                    prefix = "Stiffness scaling module invoked at time t = "
                    rest = line[len(prefix):]

                    # Split to get time and number of steps
                    if " and number of steps = " in rest:
                        time_str, nevents_str = rest.split(" and number of steps = ")
                        try:
                            time = float(time_str)
                            nevents = int(nevents_str.rstrip(':'))
                        except ValueError:
                            # If conversion fails, skip this sub-block
                            i += 1
                            continue
                    else:
                        # If the expected format is not found, skip this sub-block
                        i += 1
                        continue

                    # Initialize coefficients to 1.0 for all steps
                    coefficients = {step: 1.0 for step in steps}

                    # Move to the next line after the header
                    i += 1

                    # Traverse lines until "Updated list of downscaled steps:" is found
                    while i < n:
                        current_line = block_lines[i].strip()
                        if current_line.startswith("Updated list of downscaled steps:"):
                            break
                        i += 1

                    if i >= n:
                        # If "Updated list of downscaled steps:" is not found, skip to next sub-block
                        break

                    # Move to the lines after "Updated list of downscaled steps:"
                    i += 1

                    if i >= n:
                        # If there are no lines after the header, skip
                        break

                    updated_line = block_lines[i].strip()

                    if updated_line == "All stiffness coefficients are one":
                        # No changes needed; coefficients remain 1.0
                        i += 1
                    else:
                        # Parse each line with "Elementary steps X/Y (step_name): value"
                        while i < n:
                            current_line = block_lines[i].strip()

                            if not current_line.startswith("Elementary steps"):
                                # End of the updated list
                                break

                            # Example line:
                            # "Elementary steps 3/4 (aCO_HfC): 1.0514441655341260E-002"

                            # Split the line at the colon to separate step info and value
                            if ":" in current_line:
                                step_info, value_str = current_line.split(":", 1)
                                step_info = step_info.strip()
                                value_str = value_str.strip()

                                # Extract step_name from step_info
                                # step_info format: "Elementary steps X/Y (step_name)"
                                start_idx = step_info.find('(')
                                end_idx = step_info.find(')')
                                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                                    step_name = step_info[start_idx + 1:end_idx]
                                    try:
                                        value = float(value_str)
                                        if step_name in coefficients:
                                            coefficients[step_name] = value
                                    except ValueError:
                                        # If value conversion fails, ignore and continue
                                        pass

                            # Move to the next line
                            i += 1

                    # Append the parsed data to data_dict
                    data_dict['time'].append(time)
                    data_dict['nevents'].append(nevents)
                    for step in steps:
                        data_dict[step].append(coefficients.get(step, 1.0))

                else:
                    # If the line does not start a new sub-block, move to the next line
                    i += 1

        def parse_legacy(block_lines: List[str], steps: List[str], data_dict: Dict[str, List[Any]]):
            """
            Parses sub-blocks specific to the 'legacy' algorithm and updates data_dict.

            Parameters
            ----------
            block_lines : List[str]
                Lines within the "Commencing simulation:" block.
            steps : List[str]
                List of stiffness scalable steps.
            data_dict : Dict[str, List[Any]]
                Dictionary to store parsed data.
            """
            i = 0
            n = len(block_lines)

            # Initialize current coefficients for all steps to 1.0
            current_coefficients = {step: 1.0 for step in steps}

            # Define possible sub-block headers
            sub_block_headers = [
                "Stiffness detected at time t = ",
                "Stiffness scaling possibly too aggressive at time t = ",
                "Stiffness possible at time t = "
            ]

            while i < n:
                line = block_lines[i].strip()

                # Check if the line starts with any of the sub-block headers
                if any(line.startswith(header) for header in sub_block_headers):
                    # Extract the time from the header
                    # Find the index of 't = ' and extract the float value
                    try:
                        # Find the position of 't = '
                        t_index = line.find('t = ')
                        if t_index == -1:
                            raise ValueError("Time not found in sub-block header.")

                        # Extract the part after 't = '
                        time_part = line[t_index + len('t = '):]

                        # The time value ends at the first occurrence of ':' or space
                        # Find the first occurrence of ':' or space after 't = '
                        end_index = len(time_part)
                        for sep in [':', ' ']:
                            sep_idx = time_part.find(sep)
                            if sep_idx != -1:
                                end_index = min(end_index, sep_idx)
                        time_str = time_part[:end_index]
                        time = float(time_str)
                    except ValueError:
                        # If time extraction fails, skip this sub-block
                        i += 1
                        continue

                    # Initialize coefficients for this sub-block as a copy of current_coefficients
                    coefficients = current_coefficients.copy()

                    # Assign NaN to 'nevents' as it's not available in 'legacy' algorithm
                    nevents = np.nan

                    # Move to the next line to parse the sub-block
                    i += 1

                    while i < n:
                        current_line = block_lines[i].strip()

                        # Check if we've reached the start of a new sub-block
                        if any(current_line.startswith(header) for header in sub_block_headers):
                            break

                        # Check if the line starts with 'Elementary step'
                        if current_line.startswith("Elementary step"):
                            # Example line:
                            # "Elementary step 3 - aCO_HfC_fwd (2.0376387410451285E-003). Occurred 1808 times (too fast). StiffCoeffNew/Old = 0.57043908398242493"

                            # Split the line at the first '(' to extract step name and coefficient
                            try:
                                step_part, rest = current_line.split('(', 1)
                                coeff_part, _ = rest.split(')', 1)

                                # Extract step identifier
                                # step_part format: "Elementary step X - step_name"
                                step_info = step_part.strip()
                                # Extract step_name by splitting at ' - '
                                if ' - ' in step_info:
                                    _, step_full = step_info.split(' - ', 1)
                                    # step_full format: "aCO_HfC_fwd" or similar
                                    step_name_full = step_full.strip()
                                    # We only want the base step name (e.g., "aCO_HfC" from "aCO_HfC_fwd")
                                    if step_name_full.endswith('_fwd'):
                                        step_name = step_name_full[:-4]  # Remove '_fwd'
                                    elif step_name_full.endswith('_rev'):
                                        # Skip reverse directions
                                        i += 1
                                        continue
                                    else:
                                        # If not ending with '_fwd' or '_rev', skip
                                        i += 1
                                        continue

                                    # Parse the coefficient
                                    coefficient_str = coeff_part.strip()
                                    coefficient = float(coefficient_str)

                                    # Update the coefficient for the step
                                    if step_name in coefficients:
                                        coefficients[step_name] = coefficient
                            except (ValueError, IndexError):
                                # If any parsing error occurs, skip this line
                                pass

                        # Move to the next line
                        i += 1

                    # After parsing the sub-block, update the current_coefficients
                    current_coefficients = coefficients.copy()

                    # Append the parsed data to data_dict
                    data_dict['time'].append(time)
                    data_dict['nevents'].append(nevents)
                    for step in steps:
                        data_dict[step].append(current_coefficients.get(step, 1.0))

                else:
                    # If the line does not start a sub-block header, move to the next line
                    i += 1

        # Based on the algorithm, parse the relevant sub-blocks
        if algorithm == 'prats2024':
            parse_prats2024(block_lines, stiffness_scalable_steps, data_dict)
        elif algorithm == 'legacy':
            parse_legacy(block_lines, stiffness_scalable_steps, data_dict)
        else:
            raise ValueError(f"Unsupported algorithm '{algorithm}'. Expected 'prats2024' or 'legacy'.")

        stiffness_df = pd.DataFrame(data_dict)

        return {'stiffness_scaling_coefficients': stiffness_df}

    def parse_simulation_stopped(full_lines: List[str], blocks: List[str]):
        start, end = find_block(full_lines, "Simulation stopped:", blocks)
        # For now, do nothing

    def parse_performance_facts(full_lines: List[str], blocks: List[str]) -> Dict[str, Any]:
        start, end = find_block(full_lines, "Performance facts:", blocks)
        perf_data: Dict[str, Any] = {'cpu_time': None}  # Otherwise KMCOutput will crash for unfinished simulations
        if start is not None and end is not None:
            for line in full_lines[start:end]:
                line_stripped = line.strip()
                if line_stripped.startswith("Elapsed CPU time:"):
                    # Expected format: "Elapsed CPU time:         60327.0391 seconds"
                    parts = line_stripped.split(":", 1)
                    if len(parts) == 2:
                        # Split again to remove the "seconds" part and convert the first token to float
                        time_str = parts[1].strip().split()[0]
                        try:
                            perf_data['cpu_time'] = float(time_str)
                        except ValueError:
                            perf_data['cpu_time'] = None
                    break
        return perf_data

    def parse_execution_queue_statistics(full_lines: List[str], blocks: List[str]):
        start, end = find_block(full_lines, "Execution queue statistics:", blocks)
        # For now, do nothing

    def parse_memory_usage_statistics(full_lines: List[str], blocks: List[str]):
        start, end = find_block(full_lines, "Memory usage statistics:", blocks)
        # For now, do nothing

    # Parse header to get version
    data['version'] = parse_header(lines)

    # Parse blocks
    parse_compiler_information(lines, known_blocks)
    parse_threading_information(lines, known_blocks)
    sim_data = parse_simulation_setup(lines, known_blocks)
    data.update(sim_data)
    lattice_data = parse_lattice_setup(lines, known_blocks, data['version'])
    data.update(lattice_data)
    parse_energetics_setup(lines, known_blocks)
    mech_data = parse_mechanism_setup(lines, known_blocks, data['enable_stiffness_scaling'],
                                      data['stiffness_scaling_algorithm'])
    data.update(mech_data)
    parse_preparing_simulation(lines, known_blocks)
    comm_data = parse_commencing_simulation(
        full_lines=lines,
        blocks=known_blocks,
        parse_stiffness_coefficients=parse_stiffness_coefficients,
        stiffness_scalable_steps=data.get('stiffness_scalable_steps', []),
        algorithm=data.get('stiffness_scaling_algorithm', None)
    )
    data.update(comm_data)
    parse_simulation_stopped(lines, known_blocks)
    perf_data = parse_performance_facts(lines, known_blocks)
    data.update(perf_data)
    parse_execution_queue_statistics(lines, known_blocks)
    parse_memory_usage_statistics(lines, known_blocks)

    return data
