import os
import glob
from typing import Union
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import matplotlib.ticker as mticker

from zacrostools.kmc_output import KMCOutput
from zacrostools.custom_exceptions import PlotError
from zacrostools.simulation_input import parse_simulation_input_file
from zacrostools.heatmaps.heatmap_functions import get_axis_label, extract_value


def plot_phasediagram(
        # general mandatory parameters
        ax,
        x: str,
        y: str,
        scan_path: str,
        # plot-specific optional parameters
        site_type: str = 'StTp1',
        min_coverage: Union[float, int] = 50.0,
        tick_labels: dict = None,
        weights: str = None,
        analysis_range: list = None,
        range_type: str = 'time',
        # general optional parameters
        cmap: str = "bwr",
        show_points: bool = False,
        show_colorbar: bool = True,
        auto_title: bool = False):
    """
    Plots a phase diagram heatmap using pcolormesh.
    The color represents the dominant surface species (converted to numeric values).

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axis object where the phase diagram is drawn.
    x : str
        Parameter name for the x-axis (e.g., 'pressure_X' or 'temperature').
    y : str
        Parameter name for the y-axis.
    scan_path : str
        Path to the directory containing simulation subdirectories.
    site_type : str, optional
        Site type to consider when retrieving coverage and dominant adsorbate data
        (default is 'StTp1').
    min_coverage : float or int, optional
        Minimum total coverage (%) required to assign a dominant species
        (default is 50.0).
    tick_labels : dict, optional
        Mapping of colorbar tick labels to lists of surface species.
        For example, one may pass:

            {
                '$CH_{x}$': ['CH3', 'CH3_Pt', 'CH2', 'CH2_Pt', 'CH', 'CH_Pt', 'C', 'C_Pt'],
                '$CHO/COH$': ['CHO', 'CHO_Pt', 'COH', 'COH_Pt'],
                '$CO$': ['CO', 'CO_Pt'],
                '$COOH$': ['COOH', 'COOH_Pt'],
                '$CO_{2}$': ['CO2', 'CO2_Pt'],
                '$H$': ['H', 'H_Pt'],
                '$H_{2}O$': ['H2O', 'H2O_Pt'],
                '$OH$': ['OH', 'OH_Pt'],
                '$O$': ['O', 'O_Pt']
            }

        The code automatically assigns a tick value of 0.5 for the first key, 1.5 for the second,
        2.5 for the third, etc. If not provided, the default is to parse the 'simulation_input.dat'
        file from the first simulation directory and assign each surface species its own group.
    weights : str, optional
        Weighting method for the simulation analysis (e.g., 'time', 'events', or None).
    analysis_range : list, optional
        Portion of the simulation data to analyze (default is [0, 100]).
    range_type : str, optional
        Type of range to consider in the analysis ('time' or 'nevents').
    cmap : str, optional
        Colormap to be used for the phase diagram (default is 'bwr').
    show_points : bool, optional
        If True, overlay the grid points on the phase diagram.
    show_colorbar : bool, optional
        If True, display a colorbar alongside the phase diagram.
    auto_title : bool, optional
        If True, automatically set a title for the phase diagram.

    Notes
    -----
    - The dominant surface species is only assigned if the total coverage meets or exceeds
      the specified min_coverage threshold.
    - If tick_labels is not provided, the code parses 'simulation_input.dat' from the first simulation
      directory and assigns each species to its own group (with the species name as label).
    """

    # Set default analysis range if needed
    if analysis_range is None:
        analysis_range = [0, 100]

    # Validate scan_path
    if not os.path.isdir(scan_path):
        raise ValueError(f"Scan path folder does not exist: {scan_path}")

    simulation_dirs = glob.glob(os.path.join(scan_path, "*"))
    if len(simulation_dirs) == 0:
        raise ValueError(f"Scan path folder is empty: {scan_path}")

    # If tick_labels is not provided, construct a default mapping by parsing the simulation input file.
    # We also need the actual species list for validation later.
    first_sim = simulation_dirs[0]
    input_file = os.path.join(first_sim, "simulation_input.dat")
    data = parse_simulation_input_file(input_file=input_file)
    surf_specs_names = data.get('surf_specs_names')
    if surf_specs_names is None:
        raise ValueError(f"'surf_specs_names' not found in {input_file}")

    if tick_labels is None:
        # Default: assign each species to its own group using its own name as label
        tick_labels = {species: [species] for species in sorted(surf_specs_names)}
    else:
        # Validate user-provided tick_labels against actual species
        actual = set(surf_specs_names)
        for label, species_list in tick_labels.items():
            for species in species_list:
                if species not in actual:
                    # Case A: missing but star-variant exists (e.g. selected 'O' doesn't exist but 'O*' exist)
                    if not species.endswith('*') and f"{species}*" in actual:
                        raise ValueError(
                            f"Adsorbate name '{species}' included in tick_labels not found, "
                            f"but an adsorbate exists with name '{species}*'. Please correct the surface name."
                        )
                    else:
                        # Case B: not found at all (e.g. selected 'O' doesn't exist nor does 'O*')
                        raise ValueError(
                            f"Adsorbate name '{species}' included in tick_labels not found in the simulation."
                        )

    # Construct surf_spec_values (mapping of each species to its numeric tick value)
    surf_spec_values = {}
    tick_values = []
    for i, (label, species_list) in enumerate(tick_labels.items()):
        numeric_value = i + 0.5
        tick_values.append(numeric_value)
        for species in species_list:
            surf_spec_values[species] = numeric_value

    # Prepare the list of tick labels for the colorbar (preserving the order)
    colorbar_labels = list(tick_labels.keys())

    # Initialize lists and DataFrame to store simulation data
    x_value_list, y_value_list = [], []
    df = pd.DataFrame()

    # Collect simulation data in a dataframe
    for sim_path in simulation_dirs:
        folder_name = os.path.basename(sim_path)

        # Extract x and y values
        x_value = extract_value(x, sim_path)
        y_value = extract_value(y, sim_path)
        df.loc[folder_name, "x_value"] = x_value
        df.loc[folder_name, "y_value"] = y_value
        if x_value not in x_value_list:
            x_value_list.append(x_value)
        if y_value not in y_value_list:
            y_value_list.append(y_value)

        # Initialize KMCOutput and retrieve dominant adsorbed species for the given site type
        try:
            kmc_output = KMCOutput(
                path=sim_path,
                analysis_range=analysis_range,
                range_type=range_type,
                weights=weights)
            df.loc[folder_name, "dominant_ads"] = kmc_output.dominant_ads_per_site_type[site_type]
            df.loc[folder_name, "coverage"] = kmc_output.av_total_coverage_per_site_type[site_type]
        except Exception as e:
            print(f"Warning: Could not initialize KMCOutput for {folder_name}: {e}")
            df.loc[folder_name, "dominant_ads"] = float('NaN')
            df.loc[folder_name, "coverage"] = float('NaN')

    # Determine whether x and y values are logarithmic (based on presence of 'pressure' in the variable name)
    x_is_log = "pressure" in x
    y_is_log = "pressure" in y

    # Build sorted arrays for x and y axis values
    x_value_list = np.sort(np.asarray(x_value_list))
    y_value_list = np.sort(np.asarray(y_value_list))
    x_list = np.power(10, x_value_list) if x_is_log else x_value_list
    y_list = np.power(10, y_value_list) if y_is_log else y_value_list

    # Create a 2D grid to store the numeric values corresponding to the dominant species
    z_axis = np.full((len(y_value_list), len(x_value_list)), np.nan)
    for i, x_val in enumerate(x_value_list):
        for j, y_val in enumerate(y_value_list):
            matching_indices = df[(df['x_value'] == x_val) & (df['y_value'] == y_val)].index
            if len(matching_indices) > 1:
                raise PlotError(
                    f"Several folders have the same values of {x} ({x_val}) and {y} ({y_val})")
            elif len(matching_indices) == 0:
                print(f"Warning: folder for x = {x_val} and y = {y_val} missing, NaN assigned")
            else:
                folder_name = matching_indices[0]
                # Only assign the dominant species if total coverage meets the threshold
                if df.loc[folder_name, "coverage"] >= min_coverage:
                    z_axis[j, i] = surf_spec_values[df.loc[folder_name, "dominant_ads"]]

    x_axis, y_axis = np.meshgrid(x_list, y_list)

    cp = ax.pcolormesh(x_axis, y_axis, z_axis, cmap=cmap, vmin=0, vmax=len(tick_labels))

    if show_colorbar:
        cbar = plt.colorbar(cp, ax=ax, ticks=tick_values, spacing='proportional',
                            boundaries=list(range(len(tick_labels) + 1)),
                            format=mticker.FixedFormatter(colorbar_labels))

    ax.set_xlim(np.min(x_list), np.max(x_list))
    ax.set_ylim(np.min(y_list), np.max(y_list))
    ax.set_xscale('log' if x_is_log else 'linear')
    ax.set_yscale('log' if y_is_log else 'linear')
    ax.set_xlabel(get_axis_label(x))
    ax.set_ylabel(get_axis_label(y))
    ax.set_facecolor("lightgray")

    if auto_title:
        if site_type == 'StTp1':
            title_label = "phase diagram"
        else:
            title_label = f"phase diagram ${site_type.replace('_', r'\_')}$"

        ax.set_title(
            label=title_label,
            y=1.0,
            pad=-14,
            color="w",
            path_effects=[pe.withStroke(linewidth=2, foreground="black")]
        )

    if show_points:
        ax.plot(x_axis.flatten(), y_axis.flatten(), 'w.', markersize=3)

    return cp
