import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, SymLogNorm, Normalize
from matplotlib.ticker import FuncFormatter
import matplotlib.patheffects as pe
import matplotlib.colors as colors

from zacrostools.kmc_output import KMCOutput
from zacrostools.custom_exceptions import PlotError
from zacrostools.heatmaps.heatmap_functions import get_axis_label, extract_value, convert_to_subscript


def plot_dtime(
        # general mandatory parameters
        ax,
        x: str,
        y: str,
        scan_path: str,
        # plot-specific mandatory parameter
        scan_path_ref: str,
        # plot-specific optional parameters
        difference_type: str = 'absolute',
        scale: str = 'log',
        max_dtime: float = None,
        min_dtime: float = None,
        nlevels: int = 0,
        analysis_range: list = None,
        range_type: str = 'time',
        # general optional parameters
        cmap: str = "RdYlBu",
        show_points: bool = False,
        show_colorbar: bool = True,
        auto_title: bool = False,
        sign: str = "both"):
    """
    Plot a ∆time heatmap using pcolormesh.

    This function computes the difference in simulation time between a main simulation and that of a
    reference simulation. It builds a heatmap where ∆time is defined as the difference between the total
    simulation time of the main simulation and that of the reference simulation. When `difference_type`
    is 'relative', the difference is computed in percent.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axis object where the plot is drawn.
    x : str
        Parameter name for the x-axis.
    y : str
        Parameter name for the y-axis.
    scan_path : str
        Path to the main simulation directories.
    scan_path_ref : str
        Path to the reference simulation directories.
    difference_type : str, optional
        Type of time difference to compute. Must be either 'absolute' (default) or 'relative'.
        - 'absolute': ∆time = time (main) - time (reference).
        - 'relative': ∆time = (time (main) - time (reference)) / |time (reference)|
                      (if time (reference) is 0, NaN is assigned).
    scale : str, optional
        Type of color scaling for the heatmap. If 'log' (default), logarithmic scaling is used.
    max_dtime : float, optional
        Maximum absolute value for time differences.
    min_dtime : float, optional
        Minimum nonzero absolute value threshold for time differences. If not provided, it defaults to max_dtime/1.0e3
        for absolute differences and to 1 for relative differences.
    nlevels : int, optional
        If 0 (the default), continuous normalization is used. Otherwise, nlevels must be a positive odd integer
        (3 or higher) that defines the number of discrete boundaries (ensuring zero is centered).
    analysis_range : list, optional
        Portion of the simulation data to analyze (default: [0, 100]).
    range_type : str, optional
        Type of range to consider in the analysis (e.g., 'time' or 'nevents').
    cmap : str, optional
        Colormap to be used for the heatmap (default: 'RdYlBu').
    show_points : bool, optional
        If True, overlay grid points on the heatmap.
    show_colorbar : bool, optional
        If True, display a colorbar alongside the heatmap.
    auto_title : bool, optional
        If True, automatically set a title for the plot.
    sign : str, optional
        Which sign of ∆time to include: 'both' (default), 'positive', or 'negative'.

    Notes
    -----
    - The function reads simulation data from the provided main and reference directories.
    - It computes the total simulation time by taking the difference between the last and first time points.
    - For both absolute and relative differences, the color range is set symmetrically from –abs_max to +abs_max so that
      zero is centered.
    - When `scale` is 'log', if discretization is enabled (nlevels ≠ 0) the positive boundaries are generated using
      logarithmic spacing (and mirrored for negative values). If discretization is disabled (nlevels=0), a continuous
      normalization is used (via SymLogNorm if data include both positive and negative values).
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

        # Retrieve simulation times and compute the difference
        try:
            kmc_output = KMCOutput(
                path=sim_path,
                analysis_range=analysis_range,
                range_type=range_type)
            time = max(kmc_output.time[-1] - kmc_output.time[0], 0)
            df.loc[folder_name, "time"] = time

            kmc_output_ref = KMCOutput(
                path=ref_path,
                analysis_range=analysis_range,
                range_type=range_type)
            time_ref = max(kmc_output_ref.time[-1] - kmc_output_ref.time[0], 0)
            df.loc[folder_name, "time_ref"] = time_ref

            # Compute difference according to the chosen difference_type.
            if difference_type == 'absolute':
                df.loc[folder_name, "dtime"] = time - time_ref
            elif difference_type == 'relative':
                if time_ref != 0:
                    df.loc[folder_name, "dtime"] = (time - time_ref) / abs(time_ref)
                else:
                    df.loc[folder_name, "dtime"] = np.nan
            else:
                raise ValueError("difference_type parameter must be either 'absolute' or 'relative'")
        except Exception as e:
            print(f"Warning: Could not initialize KMCOutput for {folder_name}: {e}")
            df.loc[folder_name, "time"] = float('NaN')
            df.loc[folder_name, "time_ref"] = float('NaN')

    # Build sorted arrays for x and y axis values
    x_value_list = np.sort(np.asarray(x_value_list))
    y_value_list = np.sort(np.asarray(y_value_list))
    x_list = np.power(10, x_value_list) if x_is_log else x_value_list
    y_list = np.power(10, y_value_list) if y_is_log else y_value_list

    # Create a 2D grid for dtime values
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
                if max_dtime is not None:
                    if df.loc[folder_name, "dtime"] > max_dtime:
                        z_axis[j, i] = max_dtime
                    elif df.loc[folder_name, "dtime"] < -max_dtime:
                        z_axis[j, i] = -max_dtime
                    else:
                        z_axis[j, i] = df.loc[folder_name, "dtime"]
                else:
                    z_axis[j, i] = df.loc[folder_name, "dtime"]

    x_axis, y_axis = np.meshgrid(x_list, y_list)

    if sign not in ("both", "positive", "negative"):
        raise ValueError("`sign` must be 'both', 'positive' or 'negative'")
    if sign == "positive":
        z_axis[z_axis <= min_dtime] = min_dtime
    elif sign == "negative":
        z_axis[z_axis >= max_dtime] = max_dtime

    # --- Determine normalization parameters ---
    computed_abs_max = max(np.abs(np.nanmin(z_axis)), np.abs(np.nanmax(z_axis)))
    if difference_type == 'absolute':
        if max_dtime is None:
            exponent = np.ceil(np.log10(computed_abs_max))
            max_dtime = 10 ** exponent
        if min_dtime is None:
            min_dtime = max_dtime / 1.0e3
        abs_max = max_dtime
    elif difference_type == 'relative':
        if max_dtime is None:
            max_dtime = 100  # default to 100 for relative differences
        if min_dtime is None:
            min_dtime = 1
        abs_max = max_dtime
    else:
        raise ValueError("difference_type must be 'absolute' or 'relative'")

    # --- Choose normalization: continuous if nlevels == 0, discrete otherwise ---
    levels = None
    if nlevels == 0:
        # Continuous normalization.
        if scale == 'lin':
            norm = Normalize(vmin=-abs_max, vmax=abs_max)
        elif scale == 'log':
            finite = z_axis[np.isfinite(z_axis)]
            if finite.size and np.all(finite > 0):
                norm = LogNorm(vmin=min_dtime, vmax=abs_max)
            elif finite.size and np.all(finite < 0):
                norm = LogNorm(vmin=-abs_max, vmax=-min_dtime)
            else:
                norm = SymLogNorm(linthresh=min_dtime, linscale=1.0,
                                  vmin=-abs_max, vmax=+abs_max, base=10)
        else:
            raise ValueError("scale parameter must be either 'log' or 'lin'")
    else:
        # Discrete normalization is requested.
        if (not isinstance(nlevels, int)) or (nlevels < 3) or (nlevels % 2 == 0):
            raise ValueError("nlevels must be either 0 or a positive odd integer (>=3)")
        if scale == 'lin':
            levels = np.linspace(-abs_max, abs_max, nlevels)
        elif scale == 'log':
            positive_levels = np.logspace(np.log10(min_dtime), np.log10(abs_max), (nlevels - 1) // 2)
            levels = np.concatenate((-positive_levels[::-1], [0], positive_levels))
        else:
            raise ValueError("scale parameter must be either 'log' or 'lin'")
        norm = colors.BoundaryNorm(levels, ncolors=plt.get_cmap(cmap).N, clip=True)

    # --- Create pcolormesh plot ---
    cp = ax.pcolormesh(x_axis, y_axis, z_axis, cmap=cmap, norm=norm)

    if show_colorbar:
        if levels is not None:
            cbar = plt.colorbar(cp, ax=ax, boundaries=levels, ticks=levels)
        else:
            cbar = plt.colorbar(cp, ax=ax)
        # --- Custom formatter for colorbar tick labels ---
        if scale == 'log':
            def log_formatter(x, pos):
                if np.isclose(x, 0):
                    return '0'
                exponent_cb = int(np.floor(np.log10(abs(x))))
                if np.isclose(abs(x), 10 ** exponent_cb, rtol=1e-5, atol=1e-8):
                    return r'$+10^{%d}$' % exponent_cb if x > 0 else r'$-10^{%d}$' % exponent_cb
                else:
                    return r'$%+1.1e$' % x
            formatter = FuncFormatter(log_formatter)
        else:
            formatter = FuncFormatter(lambda x, pos: f'+{x:.1f}' if x > 0 else f'{x:.1f}')
        cbar.ax.yaxis.set_major_formatter(formatter)
        # ---------------------------------------------------

    ax.set_xlim(np.min(x_list), np.max(x_list))
    ax.set_ylim(np.min(y_list), np.max(y_list))
    ax.set_xscale('log' if x_is_log else 'linear')
    ax.set_yscale('log' if y_is_log else 'linear')
    ax.set_xlabel(get_axis_label(x))
    ax.set_ylabel(get_axis_label(y))
    ax.set_facecolor("lightgray")

    if auto_title:
        if difference_type == 'absolute':
            label = "∆Time (abs.)"
        else:
            label = "∆Time (rel.)"
        ax.set_title(
            label=label,
            y=1.0,
            pad=-14,
            color="w",
            path_effects=[pe.withStroke(linewidth=2, foreground="black")]
        )

    if show_points:
        ax.plot(x_axis.flatten(), y_axis.flatten(), 'w.', markersize=3)

    return cp

