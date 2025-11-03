import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import matplotlib.ticker as mticker

from zacrostools.detect_issues import detect_issues
from zacrostools.custom_exceptions import PlotError
from zacrostools.heatmaps.heatmap_functions import get_axis_label, extract_value


def plot_issues(
        # general mandatory parameters
        ax,
        x: str,
        y: str,
        scan_path: str,
        # plot-specific mandatory parameters
        analysis_range: list,
        # plot-specific optional parameters
        range_type: str = 'time',
        # detect_issues optional parameters (pass-through)
        energy_slope_thr: float = 5.0e-10,
        time_r2_thr: float = 0.95,
        max_points: int = 100,
        # general optional parameters
        cmap: str = "RdYlGn",
        show_points: bool = False,
        show_colorbar: bool = True,
        auto_title: bool = False,
        verbose=False):
    """
    Plots an issues heatmap using pcolormesh.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axis object where the heatmap is drawn.
    x : str
        Parameter for the x-axis.
    y : str
        Parameter for the y-axis.
    scan_path : str
        Path to the directory containing simulation subdirectories.
    analysis_range : list
        Portion of the simulation data to analyze (e.g., [0, 100]). If None, defaults to [0, 100].
    range_type : str, optional
        Type of range to consider in the analysis ('time' or 'nevents').
    energy_slope_thr : float, optional
        Threshold for the absolute energy slope used by `detect_issues`
        (default is 5.0e-10).
    time_r2_thr : float, optional
        R² threshold for the linearity of time vs. events used by
        `detect_issues` (default is 0.95).
    max_points : int, optional
        Maximum number of data points sampled by `detect_issues`
        (default is 100).
    cmap : str, optional
        Colormap for the heatmap (default is "RdYlGn").
    show_points : bool, optional
        If True, overlay grid points on the heatmap (default is False).
    show_colorbar : bool, optional
        If True, add a colorbar to the plot (default is True).
    auto_title : bool, optional
        If True, set an automatic title for the plot (default is False).
    verbose : bool, optional
        If True, print the paths of simulations with detected issues (default is False).


    Notes
    -----
    - If analysis_range is None, it is set internally to [0, 100].
    - A simulation with issues is assigned a value of -0.5; one without issues is assigned 0.5.
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

        # Retrieve issues
        try:
            df.loc[folder_name, "issues"] = detect_issues(
                job_path=sim_path,
                analysis_range=analysis_range,
                range_type=range_type,
                energy_slope_thr=energy_slope_thr,
                time_r2_thr=time_r2_thr,
                max_points=max_points)
            if df.loc[folder_name, "issues"] and verbose:
                print(f"Issue detected: {sim_path}")
        except Exception as e:
            print(f"Warning: Could not initialize KMCOutput for {folder_name}: {e}")
            df.loc[folder_name, "issues"] = float('NaN')

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

                if not np.isnan(df.loc[folder_name, "issues"]):
                    z_axis[j, i] = -0.5 if df.loc[folder_name, "issues"] else 0.5

    x_axis, y_axis = np.meshgrid(x_list, y_list)

    cp = ax.pcolormesh(x_axis, y_axis, z_axis, cmap=cmap, vmin=-1, vmax=1)

    if show_colorbar:
        cbar = plt.colorbar(cp, ax=ax, ticks=[-0.5, 0.5], spacing='proportional',
                            boundaries=[-1, 0, 1],
                            format=mticker.FixedFormatter(['Yes', 'No']))

    ax.set_xlim(np.min(x_list), np.max(x_list))
    ax.set_ylim(np.min(y_list), np.max(y_list))
    ax.set_xscale('log' if x_is_log else 'linear')
    ax.set_yscale('log' if y_is_log else 'linear')
    ax.set_xlabel(get_axis_label(x))
    ax.set_ylabel(get_axis_label(y))
    ax.set_facecolor("lightgray")

    if auto_title:
        ax.set_title(
            label="issues",
            y=1.0,
            pad=-14,
            color="w",
            path_effects=[pe.withStroke(linewidth=2, foreground="black")]
        )

    if show_points:
        ax.plot(x_axis.flatten(), y_axis.flatten(), 'w.', markersize=3)

    return cp
