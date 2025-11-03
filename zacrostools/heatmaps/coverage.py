import os
import glob
from typing import Union, Optional
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

from zacrostools.kmc_output import KMCOutput
from zacrostools.custom_exceptions import PlotError
from zacrostools.heatmaps.heatmap_functions import get_axis_label, extract_value


def plot_coverage(
        # general mandatory parameters
        ax,
        x: str,
        y: str,
        scan_path: str,
        # plot-specific mandatory parameters
        surf_spec: Union[str, list] = None,
        # plot-specific optional parameters
        site_type: str = 'StTp1',
        weights: str = None,
        levels: Optional[Union[list, np.ndarray]] = np.linspace(0, 100, 11, dtype=int),
        analysis_range: list = None,
        range_type: str = 'time',
        # general optional parameters
        cmap: str = "Oranges",
        show_points: bool = False,
        show_colorbar: bool = True,
        auto_title: bool = False):
    """
    Plots a coverage heatmap using a contourf plot.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axis object where the plot is drawn.
    x : str
        Parameter name for the x-axis (e.g., 'pressure_X' or 'temperature').
    y : str
        Parameter name for the y-axis.
    scan_path : str
        Path to the directory containing simulation subdirectories.
    surf_spec : str or list, optional
        Surface species for which coverage is calculated. Use 'all' to plot total coverage.
    site_type : str, optional
        Site type to consider when retrieving coverage (default is 'StTp1').
    weights : str, optional
        Weighting method for the simulation analysis (e.g., 'time', 'events', or None).
    levels : list or np.ndarray, optional
        Contour levels for the plot (default is np.linspace(0, 100, 11, dtype=int)). When
        provided, the coverage values are clipped to the minimum and maximum values in this list.
    analysis_range : list, optional
        Portion of the simulation data to analyze (default is [0, 100]).
    range_type : str, optional
        Type of range to consider in the analysis ('time' or 'nevents').
    cmap : str, optional
        Colormap to be used for the contour plot (default is 'Oranges').
    show_points : bool, optional
        If True, overlay the grid points on the heatmap.
    show_colorbar : bool, optional
        If True, display a colorbar alongside the heatmap.
    auto_title : bool, optional
        If True, automatically set the plot title.

    Notes
    -----
    - When computing coverage, if `surf_spec` is not 'all', a list of surface species can be provided.
      For a single surface species, a string can be used. Coverage values for multiple species are summed.
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

    # Determine whether x and y values are logarithmic (based on presence of 'pressure' in the variable name)
    x_is_log = "pressure" in x
    y_is_log = "pressure" in y

    # Initialize lists and DataFrame to store data
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

        # Initialize KMCOutput and retrieve coverage for the given surf_spec
        try:
            kmc_output = KMCOutput(
                path=sim_path,
                analysis_range=analysis_range,
                range_type=range_type,
                weights=weights)
            if surf_spec == 'all':
                df.loc[folder_name, "coverage"] = kmc_output.av_total_coverage_per_site_type[site_type]
            else:
                coverage = 0.0
                if isinstance(surf_spec, str):
                    surf_spec = [surf_spec]
                for ads in surf_spec:
                    coverage += kmc_output.av_coverage_per_site_type[site_type].get(ads, 0.0)
                df.loc[folder_name, "coverage"] = coverage
        except Exception as e:
            print(f"Warning: Could not initialize KMCOutput for {folder_name}: {e}")
            df.loc[folder_name, "coverage"] = float('NaN')

    # Build sorted arrays for x and y axis values
    x_value_list = np.sort(np.asarray(x_value_list))
    y_value_list = np.sort(np.asarray(y_value_list))
    x_list = np.power(10, x_value_list) if x_is_log else x_value_list
    y_list = np.power(10, y_value_list) if y_is_log else y_value_list

    # Create a 2D grid
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

                z_axis[j, i] = df.loc[folder_name, "coverage"]

    x_axis, y_axis = np.meshgrid(x_list, y_list)

    # Create a contourf plot using logarithmic normalization
    cp = ax.contourf(x_axis, y_axis, z_axis, levels=levels, cmap=cmap,
                     vmin=min(levels), vmax=max(levels))

    if show_colorbar:
        cbar = plt.colorbar(cp, ax=ax)

    ax.set_xlim(np.min(x_list), np.max(x_list))
    ax.set_ylim(np.min(y_list), np.max(y_list))
    ax.set_xscale('log' if x_is_log else 'linear')
    ax.set_yscale('log' if y_is_log else 'linear')
    ax.set_xlabel(get_axis_label(x))
    ax.set_ylabel(get_axis_label(y))
    ax.set_facecolor("lightgray")

    if auto_title:
        if site_type == 'StTp1':
            title_label = "coverage (%)"
        else:
            title_label = f"coverage ${site_type.replace('_', r'\_')}$ (%)"

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
