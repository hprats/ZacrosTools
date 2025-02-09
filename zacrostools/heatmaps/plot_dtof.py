import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, SymLogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable

from zacrostools.kmc_output import KMCOutput
from zacrostools.heatmaps.heatmap_functions import get_axis_label, extract_value


def plot_dtof(
        # general mandatory parameters
        ax,
        x: str,
        y: str,
        scan_path: str,
        # plot-specific mandatory parameters
        gas_spec: str = None,
        scan_path_ref: str = None,
        # plot-specific optional parameters
        max_dtof: float = None,
        min_dtof: float = None,
        weights: str = None,
        analysis_range: list = None,
        range_type: str = 'time',
        # general optional parameters
        cmap: str = "RdYlBu",
        show_points: bool = False,
        show_colorbar: bool = True,
        auto_title: bool = False):
    """
    Plots a ∆TOF (delta TOF) heatmap using pcolormesh.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axis object for the plot.
    scan_path : str
        Path to the main simulation directories.
    scan_path_ref : str
        Path to the reference simulation directories.
    x : str
        Parameter for the x-axis.
    y : str
        Parameter for the y-axis.
    gas_spec : str
        Gas species for which TOF is computed.
    min_dtof : float, optional
        Minimum absolute value threshold for TOF differences.
    max_dtof : float, optional
        Maximum absolute value for TOF differences.
    analysis_range : list, optional
        Portion of the simulation to analyze (default: [0, 100]).
    range_type : str, optional
        Type of range ('time' or 'nevents').
    weights : str, optional
        Weighting method.
    cmap : str, optional
        Colormap (default: 'RdYlBu').
    show_points : bool, optional
        If True, overlay grid points.
    show_colorbar : bool, optional
        If True, display a colorbar.

    Returns
    -------
    cp : QuadMesh
        The pcolormesh object.
    """

    # Set default analysis range if needed
    if analysis_range is None:
        analysis_range = [0, 100]

    # Validate scan_path and scan_path_ref
    if not os.path.isdir(scan_path):
        raise ValueError(f"Scan path folder does not exist: {scan_path}")
    if not os.path.isdir(scan_path_ref):
        raise ValueError(f"Reference scan path folder does not exist: {scan_path_ref}")

    simulation_dirs = glob.glob(os.path.join(scan_path, "*"))
    if len(simulation_dirs) == 0:
        raise ValueError(f"Scan path folder is empty: {scan_path}")

    simulation_ref_dirs = glob.glob(os.path.join(scan_path_ref, "*"))
    if len(simulation_ref_dirs) == 0:
        raise ValueError(f"Scan path folder is empty: {scan_path_ref}")

    # Determine whether x and y values are logarithmic (based on presence of 'pressure' in the variable name)
    x_is_log = "pressure" in x
    y_is_log = "pressure" in y

    # Initialize lists and DataFrame to store data
    x_value_list, y_value_list = [], []
    df = pd.DataFrame()


    # Loop over simulation directories (using matching folder names in the reference directory)
    for sim_path in sim_dirs:
        folder_name = os.path.basename(sim_path)
        ref_path = os.path.join(scan_path_ref, folder_name)
        if not os.path.isfile(os.path.join(sim_path, "general_output.txt")):
            print(f"Files not found: {folder_name}/general_output.txt")
            continue
        if not os.path.isfile(os.path.join(ref_path, "general_output.txt")):
            print(f"Reference files not found for: {folder_name}")
            continue

        try:
            kmc_output = KMCOutput(path=sim_path, analysis_range=analysis_range, range_type=range_type, weights=weights)
            kmc_output_ref = KMCOutput(path=ref_path, analysis_range=analysis_range, range_type=range_type,
                                       weights=weights)
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
            tof = kmc_output.tof[gas_spec]
            tof_ref = kmc_output_ref.tof[gas_spec]
        except Exception as e:
            print(f"Warning: Issue accessing TOF data for {folder_name}: {e}")
            continue

        dtof = tof - tof_ref
        data[folder_name] = {"x_value": x_val, "y_value": y_val, "dtof": dtof}

    if not data:
        raise ValueError("No valid simulation data found for delta TOF plotting.")

    x_array = np.sort(np.array(x_values))
    y_array = np.sort(np.array(y_values))
    x_list = np.power(10, x_array) if x_is_log else x_array
    y_list = np.power(10, y_array) if y_is_log else y_array

    # Build the grid for the ∆TOF values
    z_axis = np.full((len(y_array), len(x_array)), np.nan)
    df = pd.DataFrame.from_dict(data, orient="index")
    for i, xv in enumerate(x_array):
        for j, yv in enumerate(y_array):
            matching = df[(df['x_value'] == xv) & (df['y_value'] == yv)]
            if len(matching) > 1:
                raise ValueError(f"Multiple simulations for x = {xv} and y = {yv}")
            elif len(matching) == 1:
                z_axis[j, i] = matching.iloc[0]['dtof']
            else:
                print(f"Warning: No simulation for x = {xv} and y = {yv}")

    x_axis, y_axis = np.meshgrid(x_list, y_list)

    # Determine normalization parameters based on the absolute values in the grid
    if max_dtof is None:
        max_val = np.nanmax(np.abs(z_axis))
        if max_val == 0:
            max_dtof = 1.0
        else:
            exponent = np.ceil(np.log10(max_val))
            max_dtof = 10 ** exponent
    if min_dtof is None:
        min_dtof = max_dtof / 1.0e4
    min_dtof = min(min_dtof, max_dtof)
    abs_max = max_dtof

    if np.all(z_axis >= 0):
        norm = LogNorm(vmin=max(np.nanmin(z_axis[z_axis > 0]), min_dtof), vmax=abs_max)
    elif np.all(z_axis <= 0):
        norm = LogNorm(vmin=min(np.nanmax(z_axis[z_axis < 0]), -abs_max), vmax=-min_dtof)
    else:
        norm = SymLogNorm(linthresh=min_dtof, linscale=1.0, vmin=-abs_max, vmax=abs_max, base=10)

    cp = ax.pcolormesh(x_axis, y_axis, z_axis, cmap=cmap, norm=norm)

    if show_colorbar:
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        plt.colorbar(cp, cax=cax)

    ax.set_xscale('log' if x_is_log else 'linear')
    ax.set_yscale('log' if y_is_log else 'linear')
    ax.set_xlabel(get_axis_label(x))
    ax.set_ylabel(get_axis_label(y))
    ax.set_facecolor("lightgray")

    if show_points:
        ax.plot(x_axis.flatten(), y_axis.flatten(), 'k.', markersize=3)

    return cp
