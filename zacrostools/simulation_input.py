from pathlib import Path
from typing import Union, Dict, Any


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
