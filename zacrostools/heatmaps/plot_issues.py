import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from mpl_toolkits.axes_grid1 import make_axes_locatable

from zacrostools.kmc_output import KMCOutput
from zacrostools.detect_issues import detect_issues
from zacrostools.heatmaps.heatmap_functions import get_axis_label, extract_value


def plot_issues(ax, scan_path, x, y, analysis_range=None, range_type='time',
                weights=None, cmap=None, tick_values=None, tick_labels=None,
                show_points=False, show_colorbar=True, auto_title=False, verbose=False):
    """
    Plots an issues heatmap using pcolormesh.

    Each simulation is checked for issues via detect_issues. Simulations with issues
    are assigned a value of -0.5 and those without issues 0.5.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axis object for the plot.
    scan_path : str
        Path to the simulation directories.
    x : str
        Parameter for the x-axis.
    y : str
        Parameter for the y-axis.
    analysis_range : list, optional
        Portion of the simulation to analyze (default: [0, 100]).
    range_type : str, optional
        Type of range ('time' or 'nevents').
    weights : str, optional
        Weighting method.
    cmap : str, optional
        Colormap (default: 'RdYlGn').
    tick_values : list, optional
        Tick values for the colorbar (default: [-0.5, 0.5]).
    tick_labels : list, optional
        Tick labels for the colorbar (default: ['Yes', 'No']).
    show_points : bool, optional
        If True, grid points are overlaid.
    show_colorbar : bool, optional
        If True, a colorbar is added.
    auto_title : bool, optional
        If True, an automatic title is set.
    verbose : bool, optional
        If True, prints the paths of simulations with issues.

    Returns
    -------
    cp : QuadMesh
        The pcolormesh plot object.
    """
    if analysis_range is None:
        analysis_range = [0, 100]
    if cmap is None:
        cmap = "RdYlGn"
    if tick_values is None:
        tick_values = [-0.5, 0.5]
    if tick_labels is None:
        tick_labels = ['Yes', 'No']

    if not os.path.isdir(scan_path):
        raise ValueError(f"Scan path folder does not exist: {scan_path}")

    x_is_log = "pressure" in x
    y_is_log = "pressure" in y

    x_values = []
    y_values = []
    data = {}

    sim_dirs = glob.glob(os.path.join(scan_path, "*"))
    if not sim_dirs:
        raise ValueError(f"Scan path folder is empty: {scan_path}")

    for sim_path in sim_dirs:
        folder_name = os.path.basename(sim_path)
        general_output_file = os.path.join(sim_path, "general_output.txt")
        if not os.path.isfile(general_output_file):
            print(f"Files not found: {folder_name}/general_output.txt")
            continue

        try:
            kmc_output = KMCOutput(path=sim_path, analysis_range=analysis_range,
                                   range_type=range_type, weights=weights)
        except Exception as e:
            print(f"Warning: Could not initialize KMCOutput for {folder_name}: {e}")
            continue

        try:
            x_val = extract_value(x, sim_path)
            y_val = extract_value(y, sim_path)
        except Exception as e:
            print(f"Warning: {e}")
            continue

        if x_val not in x_values:
            x_values.append(x_val)
        if y_val not in y_values:
            y_values.append(y_val)

        try:
            issue_flag = detect_issues(path=sim_path, analysis_range=analysis_range)
        except Exception as e:
            print(f"Warning: Could not detect issues for {folder_name}: {e}")
            issue_flag = None

        if issue_flag is None:
            value = np.nan
        else:
            value = -0.5 if issue_flag else 0.5
            if issue_flag and verbose:
                print(f"Issue detected: {sim_path}")

        data[folder_name] = {"x_value": x_val, "y_value": y_val, "issues": value}

    if not data:
        raise ValueError("No valid simulation data found for issues plotting.")

    x_array = np.sort(np.array(x_values))
    y_array = np.sort(np.array(y_values))
    x_list = np.power(10, x_array) if x_is_log else x_array
    y_list = np.power(10, y_array) if y_is_log else y_array

    # Build grid for issues values.
    z_axis = np.full((len(y_array), len(x_array)), np.nan)
    df = pd.DataFrame.from_dict(data, orient="index")
    for i, xv in enumerate(x_array):
        for j, yv in enumerate(y_array):
            matching = df[(df['x_value'] == xv) & (df['y_value'] == yv)]
            if len(matching) > 1:
                raise ValueError(f"Multiple simulations found for x = {xv} and y = {yv}")
            elif len(matching) == 1:
                z_axis[j, i] = matching.iloc[0]['issues']
            else:
                print(f"Warning: No simulation for x = {xv} and y = {yv}")

    x_axis, y_axis = np.meshgrid(x_list, y_list)

    cp = ax.pcolormesh(x_axis, y_axis, z_axis, cmap=cmap, vmin=-1, vmax=1)

    if show_colorbar:
        cbar = plt.colorbar(cp, ax=ax, ticks=tick_values, spacing='proportional',
                            boundaries=[-1, 0, 1],
                            format=mticker.FixedFormatter(tick_labels))

    ax.set_xscale('log' if x_is_log else 'linear')
    ax.set_yscale('log' if y_is_log else 'linear')
    ax.set_xlabel(get_axis_label(x))
    ax.set_ylabel(get_axis_label(y))
    ax.set_facecolor("lightgray")

    if auto_title:
        ax.set_title("Issues", y=1.0, pad=-14)

    if show_points:
        ax.plot(x_axis.flatten(), y_axis.flatten(), 'k.', markersize=3)

    return cp
