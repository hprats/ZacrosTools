import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Union, Optional
import matplotlib.patheffects as pe
from matplotlib.colors import LogNorm

from zacrostools.kmc_output import KMCOutput
from zacrostools.custom_exceptions import PlotError
from zacrostools.heatmaps.heatmap_functions import get_axis_label, extract_value


def plot_finaltime(
        # general mandatory parameters
        ax,
        x: str,
        y: str,
        scan_path: str,
        # plot-specific optional parameters
        levels: Optional[Union[list, np.ndarray]] = None,
        # general optional parameters
        cmap: str = "inferno",
        show_points: bool = False,
        show_colorbar: bool = True,
        auto_title: bool = False):
    """
    Plots a final time heatmap using a contourf plot.

    The final time (in seconds) is read from each simulation’s KMC output.
    Logarithmic normalization (LogNorm) is applied.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axis object where the plot is drawn.
    x : str
        Parameter for the x-axis (e.g., 'pressure_X' or 'temperature').
    y : str
        Parameter for the y-axis.
    scan_path : str
        Path to the directory containing simulation subdirectories.
    levels : list or np.ndarray, optional
        Contour levels for the plot. If provided, normalization uses
        vmin=min(levels) and vmax=max(levels). Default is None.
    cmap : str, optional
        Colormap to be used for the plot (default is 'inferno').
    show_points : bool, optional
        If True, overlay the grid points on the heatmap. Default is False.
    show_colorbar : bool, optional
        If True, display a colorbar alongside the heatmap. Default is True.
    auto_title : bool, optional
        If True, automatically set a title for the plot. Default is False.

    Notes
    -----
    - Final time values are extracted from each simulation's KMCOutput; if a simulation
      cannot be read, NaN is assigned.
    """

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

        # Initialize KMCOutput and retrieve final time
        try:
            kmc_output = KMCOutput(path=sim_path)
            df.loc[folder_name, 'final_time'] = kmc_output.final_time
        except Exception as e:
            print(f"Warning: Could not initialize KMCOutput for {folder_name}: {e}")
            df.loc[folder_name, "final_time"] = float('NaN')

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

                z_axis[j, i] = df.loc[folder_name, "final_time"]

    x_axis, y_axis = np.meshgrid(x_list, y_list)

    if levels is not None:
        cp = ax.contourf(x_axis, y_axis, z_axis, levels=levels, cmap=cmap,
                         norm=LogNorm(vmin=min(levels), vmax=max(levels)))
    else:
        cp = ax.contourf(x_axis, y_axis, z_axis, cmap=cmap, norm=LogNorm())

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
        ax.set_title(
            label="final time",
            y=1.0,
            pad=-14,
            color="w",
            path_effects=[pe.withStroke(linewidth=2, foreground="black")]
        )

    if show_points:
        ax.plot(x_axis.flatten(), y_axis.flatten(), 'w.', markersize=3)

    return cp
