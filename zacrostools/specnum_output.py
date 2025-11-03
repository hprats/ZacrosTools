from pathlib import Path
from typing import Union, List
import numpy as np


def parse_specnum_output_file(output_file: Union[str, Path], analysis_range: List[float], range_type: str):
    """
    Parses the specnum_output.txt file.

    Parameters
    ----------
    output_file : Union[str, Path]
        Path to the specnum_output.txt file.
    analysis_range : List[float], optional
        A list of two elements `[start_percent, end_percent]` specifying the portion of the entire simulation
        to consider for analysis. The values should be between 0 and 100, representing percentages of the
        total simulated time or the total number of events, depending on `range_type`. For example,
        `[50, 100]` would analyze only the latter half of the simulation. Default is `[0.0, 100.0]`.
    range_type : str, optional
        Determines the dimension used when applying `analysis_range`:
        - `'time'`: The percentages in `analysis_range` refer to segments of the total simulated time.
        - `'nevents'`: The percentages in `analysis_range` refer to segments of the total number of simulated events.
        Default is `'time'`.
    Returns
    -------
    Tuple[np.ndarray, List[str]]
        A tuple containing:
        - data_slice: The sliced data as a NumPy array.
        - header: List of header column names.
    """
    output_file = Path(output_file)
    if not output_file.is_file():
        raise FileNotFoundError(f"Output file '{output_file}' does not exist.")

    if range_type == 'time':
        column_index = 2
    elif range_type == 'nevents':
        column_index = 1
    else:
        raise ValueError("'range_type' must be either 'time' or 'nevents'")

    if not (isinstance(analysis_range, list) and len(analysis_range) == 2):
        raise ValueError("'analysis_range' must be a list with two elements.")
    if not all(isinstance(x, (int, float)) for x in analysis_range):
        raise ValueError("Both elements in 'analysis_range' must be numbers (int or float).")
    if not (0 <= analysis_range[0] <= 100 and 0 <= analysis_range[1] <= 100):
        raise ValueError("Values in 'analysis_range' must be between 0 and 100.")
    if analysis_range[0] > analysis_range[1]:
        raise ValueError("The first value in 'analysis_range' must be less than or equal to the second value.")

    # Read the header
    with output_file.open('r') as infile:
        header_line = infile.readline()
        header = header_line.strip().split()

    # Read the data
    try:
        data = np.loadtxt(str(output_file), skiprows=1)
    except Exception as e:
        raise ValueError(f"Could not read data from '{output_file}': {e}")

    if data.size == 0:
        raise ValueError(f"No data found in '{output_file}'.")

    # Ensure data is at least 2D (in case of single row)
    if data.ndim == 1:
        data = data[np.newaxis, :]

    column = data[:, column_index]
    final_value = column[-1]

    value_initial_percent = analysis_range[0] / 100.0 * final_value
    value_final_percent = analysis_range[1] / 100.0 * final_value

    data_slice = data[(column >= value_initial_percent) & (column <= value_final_percent)]

    return data_slice, header
