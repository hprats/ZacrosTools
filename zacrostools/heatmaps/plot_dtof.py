import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, SymLogNorm
import matplotlib.patheffects as pe

from zacrostools.kmc_output import KMCOutput
from zacrostools.custom_exceptions import PlotError
from zacrostools.heatmaps.heatmap_functions import get_axis_label, extract_value, convert_to_subscript


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
        min_molec: int = 1,
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
    for sim_path in simulation_dirs:
        folder_name = os.path.basename(sim_path)
        ref_path = os.path.join(scan_path_ref, folder_name)

        # Extract x and y values
        x_value = extract_value(x, sim_path)
        y_value = extract_value(y, sim_path)
        df.loc[folder_name, "x_value"] = x_value
        df.loc[folder_name, "y_value"] = y_value
        if x_value not in x_value_list:
            x_value_list.append(x_value)
        if y_value not in y_value_list:
            y_value_list.append(y_value)

        # Initialize KMCOutputs and retrieve TOF and total production for the given gas_spec
        try:
            kmc_output = KMCOutput(
                path=sim_path,
                analysis_range=analysis_range,
                range_type=range_type,
                weights=weights)
            df.loc[folder_name, "tof"] = max(kmc_output.tof[gas_spec], 0.0)  # only consider positive TOF
            df.loc[folder_name, "total_production"] = kmc_output.total_production[gas_spec]

            kmc_output_ref = KMCOutput(
                path=ref_path,
                analysis_range=analysis_range,
                range_type=range_type,
                weights=weights)
            df.loc[folder_name, "tof_ref"] = max(kmc_output_ref.tof[gas_spec], 0.0)  # only consider positive TOF
            df.loc[folder_name, "total_production_ref"] = kmc_output_ref.total_production[gas_spec]

            df.loc[folder_name, "dtof"] = df.loc[folder_name, "tof"] - df.loc[folder_name, "tof_ref"]

        except Exception as e:
            print(f"Warning: Could not initialize KMCOutput for {folder_name}: {e}")
            df.loc[folder_name, "tof"] = float('NaN')
            df.loc[folder_name, "tof_ref"] = float('NaN')

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

                # Only assign the dtof if total production meets the threshold
                if (df.loc[folder_name, "total_production"] >= min_molec and
                        df.loc[folder_name, "total_production_ref"] >= min_molec):

                    # Apply a maximum value if max_dtof is provided
                    if max_dtof is not None:
                        if df.loc[folder_name, "dtof"] > max_dtof:
                            z_axis[j, i] = max_dtof
                        else:
                            z_axis[j, i] = df.loc[folder_name, "dtof"]
                    else:
                        z_axis[j, i] = df.loc[folder_name, "dtof"]

    x_axis, y_axis = np.meshgrid(x_list, y_list)

    # Determine normalization parameters based on the absolute values in the grid
    if max_dtof is None:
        max_val = np.nanmax(np.abs(z_axis))
        exponent = np.ceil(np.log10(max_val))
        max_dtof = 10 ** exponent  # Round up to nearest power of 10

    if min_dtof is None:
        min_dtof = max_dtof / 1.0e3

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
            label="∆TOF " + f"${convert_to_subscript(chemical_formula=gas_spec)}$",
            y=1.0,
            pad=-14,
            color="w",
            path_effects=[pe.withStroke(linewidth=2, foreground="black")]
        )

    if show_points:
        ax.plot(x_axis.flatten(), y_axis.flatten(), 'w.', markersize=3)

    return cp
