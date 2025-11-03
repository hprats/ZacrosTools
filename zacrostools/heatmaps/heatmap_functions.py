import numpy as np
from pathlib import Path
from zacrostools.simulation_input import parse_simulation_input_file


def get_axis_label(magnitude):
    """
    Returns a nicely formatted axis label given a magnitude string.
    """
    if magnitude == 'temperature':
        return "$T$ (K)"
    elif magnitude == 'total_pressure':
        return "$p_{\\mathrm{total}}$ (bar)"
    elif "pressure" in magnitude:
        gas_species = magnitude.split('_')[-1]
        formatted_gas_species = convert_to_subscript(gas_species)
        return f"$p_{{{formatted_gas_species}}}$ (bar)"
    else:
        return magnitude


def extract_value(magnitude: str, path: str) -> float:
    """
    Extracts the value for a given magnitude from the simulation input.

    Parameters
    ----------
    magnitude : str
        The magnitude (e.g. 'temperature', 'total_pressure', 'pressure_CO').
    path : str
        Path to the simulation directory (which must contain simulation_input.dat).

    Returns
    -------
    float
        The extracted value (or its logarithm when appropriate).

    Raises
    ------
    ValueError
        If the required data is not found or is invalid.
    """
    input_file_path = Path(path) / "simulation_input.dat"
    data = parse_simulation_input_file(input_file=input_file_path)

    if magnitude == 'temperature':
        temperature = data.get("temperature")
        if temperature is None:
            raise ValueError(f"Temperature not found in {input_file_path}")
        return temperature

    elif magnitude == 'total_pressure':
        total_pressure = data.get("pressure")
        if total_pressure is None:
            raise ValueError(f"Total pressure not found in {input_file_path}")
        if total_pressure <= 0:
            raise ValueError(f"Total pressure is zero or negative in {path}")
        log_total_pressure = np.log10(total_pressure)
        return round(log_total_pressure, 8)

    elif magnitude.startswith("pressure_"):
        gas_species = magnitude.split('_')[-1]
        total_pressure = data.get("pressure")
        if total_pressure is None:
            raise ValueError(f"Total pressure not found in {input_file_path}")
        if total_pressure <= 0:
            raise ValueError(f"Total pressure is zero or negative in {path}")

        gas_specs_names = data.get('gas_specs_names')
        gas_molar_fracs = data.get('gas_molar_fracs')

        if gas_specs_names is None or gas_molar_fracs is None:
            raise ValueError(f"Gas specifications or molar fractions missing in {input_file_path}")

        try:
            index = gas_specs_names.index(gas_species)
        except ValueError:
            raise ValueError(f"Gas species '{gas_species}' not found in {input_file_path}")

        molar_fraction = gas_molar_fracs[index]

        partial_pressure = total_pressure * molar_fraction
        if partial_pressure <= 0:
            raise ValueError(f"Partial pressure for {gas_species} is zero or negative in {path}")
        log_partial_pressure = np.log10(partial_pressure)
        return round(log_partial_pressure, 8)

    else:
        raise ValueError(f"Incorrect magnitude value: {magnitude}")


def convert_to_subscript(chemical_formula):
    """
    Converts numbers in a chemical formula string to a subscript format.

    For example, 'CO2' becomes 'CO_2'.
    """
    result = ''
    for char in chemical_formula:
        if char.isnumeric():
            result += f"_{char}"
        else:
            result += char
    return result
