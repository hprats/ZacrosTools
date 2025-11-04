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
from zacrostools.heatmaps.heatmap_functions import get_axis_label, extract_value


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
        auto_title: bool = False):
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
    difference_type : {'absolute', 'ratio', 'relative', 'speedup'}, default 'absolute'
        - 'absolute': ∆t = t(main) - t(ref)
        - 'relative': ∆t = (t(main) - t(ref)) / t(ref) * 100  [percent]
                      (colorbar forced to linear, centered at 0, spanning ±max_t%)
        - 'ratio':    ∆t = t(main) / t(ref)
                      (colorbar forced to logarithmic, spanning [10^{-N}, 10^{+N}], centered at 10^0)
        - 'speedup':  same ratio as above, but colorbar spans [10^{0}, 10^{+N}] (no values < 1 shown)
    scale : {'log', 'lin'}, default 'log'
        Axis scaling for the heatmap. (Forced appropriately for 'ratio', 'speedup', and 'relative' modes.)
    max_dtime, min_dtime : float, optional
        Maximum and minimum threshold for the color scale. If None, sensible defaults are chosen:
        - For absolute differences: max → next decade above data, min → max/1e3.
        - For ratio: the colorbar spans [10^{-N}, 10^{+N}] around 1, where 10^N is the
          nearest order of magnitude to `max_dtime` if provided, otherwise to the maximum ratio in data.
        - For speedup: the colorbar spans [10^{0}, 10^{+N}] where 10^N is chosen as above.
        - For relative (%): the colorbar spans [-max_dtime, +max_dtime] with default max_dtime=30 (%).
    nlevels : int, default 0
        Number of discrete color levels.
        - For 'absolute': must be odd ≥3 if >0 (to keep 0 centered).
        - For 'relative': any odd integer ≥3 if >0 (to keep 0 centered). If 0, a continuous scale
          is used and ticks are placed sensibly (e.g., every 10% by default).
        - For 'ratio': any integer ≥2 if >0.
        - For 'speedup': any integer ≥2 if >0.
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

    Notes
    -----
    - The function reads the simulated time from the provided main and reference directories and calculates ∆t.
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
                range_type=range_type
            )
            kmc_output_ref = KMCOutput(
                path=ref_path,
                analysis_range=analysis_range,
                range_type=range_type
            )
            time = max(kmc_output.time[-1] - kmc_output.time[0], 0.0)
            time_ref = max(kmc_output_ref.time[-1] - kmc_output_ref.time[0], 0.0)

            # Compute difference according to the chosen difference_type.
            if difference_type == "absolute":
                dtime_val = time - time_ref
            elif difference_type == "relative":
                dtime_val = ((time - time_ref) / time_ref * 100.0) if (time_ref != 0) else np.nan
            elif difference_type in ("ratio", "speedup"):
                dtime_val = (time / time_ref if time_ref != 0 else np.nan)
            else:
                raise ValueError(
                    "difference_type must be 'absolute', 'relative', 'ratio', or 'speedup'"
                )

            df.loc[folder_name, "dtime"] = dtime_val

        except Exception as e:
            print(f"Warning: could not process {folder_name}: {e}")
            df.loc[folder_name, ["time",
                                 "time_ref"]] = np.nan

    # Build sorted arrays for x and y axis values
    x_value_list = np.sort(np.asarray(x_value_list))
    y_value_list = np.sort(np.asarray(y_value_list))
    x_list = np.power(10, x_value_list) if x_is_log else x_value_list
    y_list = np.power(10, y_value_list) if y_is_log else y_value_list

    # Create a 2D grid
    z_axis = np.full((len(y_value_list), len(x_value_list)), np.nan)

    for i, x_val in enumerate(x_value_list):
        for j, y_val in enumerate(y_value_list):
            matches = df[(df["x_value"] == x_val) & (df["y_value"] == y_val)].index
            if len(matches) > 1:
                raise PlotError(
                    f"Several folders share {x} = {x_val} and {y} = {y_val}"
                )
            elif len(matches) == 0:
                print(
                    f"Warning: folder for x = {x_val} and y = {y_val} missing; NaN assigned"
                )
                continue

            folder = matches[0]
            dtime_val = df.loc[folder, "dtime"]

            if np.isnan(dtime_val):
                continue  # leave as NaN

            # Optional value capping (absolute vs ratio handled later when N is known)
            if (difference_type == "absolute") and (max_dtime is not None):
                if dtime_val > max_dtime:
                    dtime_val = max_dtime
                elif dtime_val < -max_dtime:
                    dtime_val = -max_dtime

            z_axis[j, i] = dtime_val

    x_axis, y_axis = np.meshgrid(x_list, y_list)

    # --- Determine normalization parameters ---
    levels = None
    relative_ticks = None  # used only for 'relative' when nlevels==0

    if difference_type == 'absolute':
        # Compute a symmetric maximum value from the grid.
        computed_abs_max = max(np.abs(np.nanmin(z_axis)), np.abs(np.nanmax(z_axis)))
        if max_dtime is None:
            exponent = np.ceil(np.log10(computed_abs_max)) if np.isfinite(
                computed_abs_max) and computed_abs_max > 0 else 0
            max_dtime = 10 ** exponent
        if min_dtime is None:
            min_dtime = max_dtime / 1.0e3
        abs_max = max_dtime

        # Normalization (continuous/discrete)
        if nlevels == 0:
            if scale == "lin":
                norm = Normalize(vmin=-abs_max, vmax=abs_max)
            elif scale == "log":
                if np.all(z_axis > 0):
                    norm = LogNorm(vmin=min_dtime, vmax=abs_max)
                elif np.all(z_axis < 0):
                    norm = LogNorm(vmin=-abs_max, vmax=-min_dtime)
                else:
                    norm = SymLogNorm(
                        linthresh=min_dtime,
                        linscale=1.0,
                        vmin=-abs_max,
                        vmax=abs_max,
                        base=10,
                    )
            else:
                raise ValueError("scale must be 'log' or 'lin'")
        else:
            if (not isinstance(nlevels, int)) or (nlevels < 3) or (nlevels % 2 == 0):
                raise ValueError("nlevels must be either 0 or a positive odd integer (≥3)")
            if scale == 'lin':
                levels = np.linspace(-abs_max, abs_max, nlevels)
            elif scale == 'log':
                positive_levels = np.logspace(np.log10(min_dtime), np.log10(abs_max), (nlevels - 1) // 2)
                levels = np.concatenate((-positive_levels[::-1], [0], positive_levels))
            else:
                raise ValueError("scale parameter must be either 'log' or 'lin'")
            norm = colors.BoundaryNorm(levels, ncolors=plt.get_cmap(cmap).N, clip=True)

    elif difference_type == 'ratio':
        # Ratio: force log scale centered at 10^0
        scale = 'log'

        # Determine data max (ratio) and choose nearest order of magnitude
        data_max = np.nanmax(z_axis)
        if not np.isfinite(data_max) or data_max <= 0:
            data_max = 1.0

        if max_dtime is None:
            N = int(np.round(np.log10(data_max)))
        else:
            N = int(np.round(np.log10(max_dtime)))
        # Use symmetric log-range [10^{-N}, 10^{+N}]
        vmin = 10.0 ** (-abs(N))
        vmax = 10.0 ** (abs(N))

        # After N is known, cap values into [10^{-N}, 10^{N}]
        for j in range(z_axis.shape[0]):
            for i in range(z_axis.shape[1]):
                val = z_axis[j, i]
                if np.isnan(val):
                    continue
                if val < vmin:
                    z_axis[j, i] = vmin
                elif val > vmax:
                    z_axis[j, i] = vmax

        if nlevels == 0:
            norm = LogNorm(vmin=vmin, vmax=vmax)
        else:
            # For ratios we don't require odd nlevels; any >=2 works. Keep behavior minimal.
            if (not isinstance(nlevels, int)) or (nlevels < 2):
                raise ValueError("For ratio mode, nlevels must be either 0 or an integer ≥ 2")
            levels = np.logspace(-abs(N), abs(N), nlevels)
            norm = colors.BoundaryNorm(levels, ncolors=plt.get_cmap(cmap).N, clip=True)

    elif difference_type == 'speedup':
        # Speedup: force log scale from 10^0 to 10^{+N}
        scale = 'log'

        # Determine data max (ratio) and choose nearest order of magnitude
        data_max = np.nanmax(z_axis)
        if not np.isfinite(data_max) or data_max <= 1.0:
            data_max = 1.0

        if max_dtime is None:
            N = int(np.round(np.log10(data_max)))
        else:
            N = int(np.round(np.log10(max_dtime)))

        # Colorbar range [10^0, 10^{+N}] (clip all <1 to 1)
        vmin = 10.0 ** 0
        vmax = 10.0 ** (abs(N))

        # Cap values into [1, 10^{N}]
        for j in range(z_axis.shape[0]):
            for i in range(z_axis.shape[1]):
                val = z_axis[j, i]
                if np.isnan(val):
                    continue
                if val < vmin:
                    z_axis[j, i] = vmin
                elif val > vmax:
                    z_axis[j, i] = vmax

        if nlevels == 0:
            norm = LogNorm(vmin=vmin, vmax=vmax)
        else:
            if (not isinstance(nlevels, int)) or (nlevels < 2):
                raise ValueError("For speedup mode, nlevels must be either 0 or an integer ≥ 2")
            levels = np.logspace(0, abs(N), nlevels)
            norm = colors.BoundaryNorm(levels, ncolors=plt.get_cmap(cmap).N, clip=True)

    else:
        # relative (%) case: force linear scale centered at 0 within ±max_dtime
        scale = 'lin'
        if max_dtime is None:
            max_dtime = 30.0  # default ±30%
        abs_max = float(max_dtime)

        # cap values to [-abs_max, +abs_max]
        for j in range(z_axis.shape[0]):
            for i in range(z_axis.shape[1]):
                val = z_axis[j, i]
                if np.isnan(val):
                    continue
                if val > abs_max:
                    z_axis[j, i] = abs_max
                elif val < -abs_max:
                    z_axis[j, i] = -abs_max

        if nlevels == 0:
            norm = Normalize(vmin=-abs_max, vmax=abs_max)
            # default ticks every 10% (example in spec)
            step = 10.0
            # Ensure symmetric ticks
            relative_ticks = np.arange(-abs_max, abs_max + 0.5 * step, step)
        else:
            if (not isinstance(nlevels, int)) or (nlevels < 3) or (nlevels % 2 == 0):
                raise ValueError("For relative mode, nlevels must be an odd integer ≥ 3")
            levels = np.linspace(-abs_max, abs_max, nlevels)
            norm = colors.BoundaryNorm(levels, ncolors=plt.get_cmap(cmap).N, clip=True)

    # --- Create pcolormesh plot ---
    cp = ax.pcolormesh(x_axis, y_axis, z_axis, cmap=cmap, norm=norm)

    if show_colorbar:
        if levels is not None:
            cbar = plt.colorbar(cp, ax=ax, boundaries=levels, ticks=levels)
        else:
            # Relative mode may define custom ticks even with continuous norm
            if difference_type == 'relative' and relative_ticks is not None:
                cbar = plt.colorbar(cp, ax=ax, ticks=relative_ticks)
            else:
                cbar = plt.colorbar(cp, ax=ax)

        # --- Custom formatter for colorbar tick labels ---
        if scale == 'log':
            if difference_type in ('ratio', 'speedup'):
                # prepend × only in speedup mode
                _with_times = (difference_type == 'speedup')

                def rel_log_formatter(x, pos, with_times=_with_times):
                    # Show [×]10^{k} at exact powers of ten
                    if x <= 0 or not np.isfinite(x):
                        return ''
                    k = int(np.round(np.log10(x)))
                    if np.isclose(x, 10 ** k, rtol=1e-5, atol=1e-12):
                        core = r'$10^{%d}$' % k
                        return (r'$\times$' + core) if with_times else core
                    # fallback for non-powers (should be rare with LogNorm ticks)
                    return (r'$\times$' + r'$%1.1e$' % x) if with_times else (r'$%1.1e$' % x)

                formatter = FuncFormatter(rel_log_formatter)
            else:
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
            if difference_type == 'relative':
                formatter = FuncFormatter(
                    lambda x, pos: (
                        "0%" if np.isclose(x, 0)
                        else f"{x:+.0f}%".replace("-", "\N{MINUS SIGN}")
                    )
                )
            else:
                formatter = FuncFormatter(
                    lambda x, pos: (
                        "0" if np.isclose(x, 0)
                        else f"{x:+.0f}".replace("-", "\N{MINUS SIGN}")
                    )
                )

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
        # make the tag reflect the actual mode
        _tag_map = {'absolute': 'abs', 'relative': 'rel', 'ratio': 'ratio', 'speedup': 'speedup'}
        _tag = _tag_map.get(difference_type, 'abs')
        label = f"$\\Delta\\mathrm{{t}}_{{{_tag}}}$"
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
