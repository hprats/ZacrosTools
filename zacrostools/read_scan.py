import os
import pandas as pd
from glob import glob
from typing import Union
from zacrostools.kmc_output import KMCOutput
from zacrostools.custom_exceptions import KMCOutputError, PlotError


def read_scan(scan_path: str,
              window_percent: Union[list, None] = None,
              window_type: str = 'time',
              weights: Union[str, None] = None) -> pd.DataFrame:
    """
    Reads the results of all KMC simulations in a given scan directory and returns a Pandas DataFrame
    containing key observables for each simulation.

    Parameters
    ----------
    scan_path : str
        Path to the directory containing subfolders, each with a KMC simulation.
    window_percent : list, optional
        A list of two elements `[initial_percent, final_percent]` specifying the window of the total simulation.
        Values should be between 0 and 100 (percentage of total simulated time or events).
        Default is `[0.0, 100.0]`.
    window_type : str, optional
        The type of window to apply when calculating averages or TOF. Can be `'time'` or `'nevents'`.
        Default is `'time'`.
    weights : str, optional
        Weights for calculating the weighted average of coverage and energy.
        Possible values are `None`, `'time'`, or `'nevents'`. Default is `None`.

    Returns
    -------
    pd.DataFrame
        A DataFrame with one row per simulation (subfolder) and columns including:
          - temperature (K)
          - pressure (bar)
          - tof for each gas species (e.g., tof_CO, tof_CO2)
          - average coverage per site type for each adsorbate (e.g., avcov_top_CO)
          - dominant adsorbate per site type (e.g., dominant_ads_top)

        The index will be the name of the subfolder.
    """

    if not os.path.isdir(scan_path):
        raise PlotError(f"Scan path folder does not exist: {scan_path}")

    subfolders = glob(f"{scan_path}/*")
    if len(subfolders) == 0:
        raise PlotError(f"Scan path folder is empty: {scan_path}")

    data_dict = {}

    for simulation_path in subfolders:
        folder_name = os.path.basename(simulation_path)

        # Check the existence of mandatory output file to confirm it's a simulation folder
        general_output_file = os.path.join(simulation_path, "general_output.txt")
        input_file = os.path.join(simulation_path, "simulation_input.dat")
        if not os.path.isfile(general_output_file) or not os.path.isfile(input_file):
            # Not a valid simulation output folder
            # We can skip or store NaNs. Here we skip
            continue

        # Try initializing KMCOutput
        try:
            kmc_output = KMCOutput(path=simulation_path, window_percent=window_percent,
                                   window_type=window_type, weights=weights)
        except (KMCOutputError, FileNotFoundError, Exception) as e:
            # If we cannot parse this simulation's output, store NaNs for it
            print(f"Warning: Could not process {folder_name}: {e}")
            continue

        # Initialize a dictionary for this simulation
        row_data = {}

        # Basic info
        row_data["temperature"] = kmc_output.temperature
        row_data["pressure"] = kmc_output.pressure

        # TOF for each gas species
        for gas_spec in kmc_output.tof:
            row_data[f"tof_{gas_spec}"] = kmc_output.tof[gas_spec]

        # Average coverage per site type for each adsorbate
        for site_type, coverage_dict in kmc_output.av_coverage_per_site_type.items():
            for surf_spec, av_cov in coverage_dict.items():
                # Replace any underscores in site_type or surf_spec if needed for readability
                row_data[f"avcov_{site_type}_{surf_spec}"] = av_cov

        # Dominant adsorbate per site type
        for site_type, dom_ads in kmc_output.dominant_ads_per_site_type.items():
            row_data[f"dominant_ads_{site_type}"] = dom_ads

        data_dict[folder_name] = row_data

    # Create DataFrame
    df = pd.DataFrame.from_dict(data_dict, orient='index')

    # Sort columns alphabetically for convenience
    # (The user can also do this sorting outside if they prefer)
    df = df.sort_index(axis=1)

    return df
