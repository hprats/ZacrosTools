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
from zacrostools.detect_issues import detect_issues


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
        difference_type: str = 'absolute',
        check_issues: str = 'none',
        scale: str = 'log',
        min_molec: int = 1,
        max_dtof: float = None,
        min_dtof: float = None,
        min_tof_ref: float = 0.0,
        nlevels: int = 0,
        weights: str = None,
        analysis_range: list = None,
        range_type: str = 'time',
        # detect_issues optional parameters (pass-through)
        energy_slope_thr: float = 5.0e-10,
        time_r2_thr: float = 0.95,
        max_points: int = 100,
        # general optional parameters
        cmap: str = "RdYlBu",
        show_points: bool = False,
        show_colorbar: bool = True,
        auto_title: bool = False, **kwargs):
    """
    Plot the change in Turnover Frequency (∆TOF) heatmap between a main simulation and a reference.

    This function reads KMC simulation outputs for a specified gas species from both a main set of
    directories (`scan_path`) and a reference set (`scan_path_ref`), computes the TOF for each, and
    then builds a 2D heatmap of the difference (∆TOF). It supports absolute differences or relative
    differences, and can optionally mask out any simulations flagged as having issues.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Matplotlib axis to draw the heatmap on.
    x, y : str
        Names of the parameters defining the horizontal and vertical axes (e.g., 'pressure_CH4',
        'pressure_CO2'). If the string contains 'pressure', the respective axis will be logarithmic.
    scan_path : str
        Path to the folder containing the main simulation subdirectories.
    gas_spec : str, optional
        Gas species key (e.g., 'H2', 'CO') for which TOF is computed.
    scan_path_ref : str, optional
        Path to the folder containing reference simulation subdirectories (must match names).
    difference_type : {'absolute', 'relative'}, default 'absolute'
        - 'absolute': ∆TOF = TOF(main) - TOF(ref)
        - 'relative': ∆TOF = | TOF(main) / TOF(ref) |
          In this mode, the colorbar is always logarithmic and centered at 10^0 (i.e., ratio 1).
    check_issues : {'none','both','main','ref'}, default 'none'
        Which runs `detect_issues` on:
        - 'none' → neither
        - 'both' → both main and ref
        - 'main' → only the main scan
        - 'ref'  → only the reference scan
    scale : {'log', 'lin'}, default 'log'
        Axis scaling for the heatmap. (Forced to 'log' if difference_type='relative'.)
    min_molec : int, default 1
        Minimum total production threshold for both main and reference runs; below this, cell
        is masked.
    max_dtof, min_dtof : float, optional
        Maximum and minimum threshold for the color scale. If None, sensible defaults are chosen:
        - For absolute differences: max → next decade above data, min → max/1e3.
        - For relative (ratio): the colorbar spans [10^{-N}, 10^{+N}] around 1, where 10^N is the
          nearest order of magnitude to `max_dtof` if provided, otherwise to the maximum ratio in data.
    min_tof_ref : float, optional
        Minimum TOF threshold for the reference run. If nonzero and the reference TOF is below
        this value, the corresponding cell is masked (NaN). Default is 0.0.
    nlevels : int, default 0
        Number of discrete color levels (must be odd ≥3 for absolute; any int ≥2 for relative). If 0,
        continuous normalization is used.
    weights : str, optional
        Weighting mode passed to KMCOutput ('time', 'events', or None).
    analysis_range : list of two floats, default [0,100]
        Percentage of simulation range to analyze (start, end).
    range_type : {'time', 'nevents'}, default 'time'
        Whether analysis_range refers to simulation time or number of events.
    energy_slope_thr : float, optional
        Threshold for the absolute energy slope used by `detect_issues` (default is 5.0e-10).
    time_r2_thr : float, optional
        R² threshold for the linearity of time vs. events used by `detect_issues` (default is 0.95).
    max_points : int, optional
        Maximum number of data points sampled by `detect_issues` (default is 100).
    cmap : str, default 'RdYlBu'
        Colormap for the heatmap.
    show_points : bool, default False
        If True, overlays scatter points at each grid location.
    show_colorbar : bool, default True
        Whether to draw a colorbar.
    auto_title : bool, default False
        If True, automatically set the plot title indicating ∆TOF and species.

    Notes
    -----
    - The function reads simulation data from the provided main and reference directories. It computes the TOF
      for a given gas species in both sets of simulations and calculates ∆TOF.
    """
    # Parameter removal notice
    if 'percent' in kwargs:
        raise ValueError("'percent' is not supported for dtof since v2.10; relative ∆TOF is now defined as |TOF(main)/TOF(ref)| (unitless ratio).")

    # Set default analysis range if needed
    if analysis_range is None:
        analysis_range = [0, 100]

    if check_issues not in ('none', 'both', 'main', 'ref'):
        raise ValueError(f"Incorrect value for check_issues: {check_issues}")

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

        # Compute TOF and ∆TOF
        try:
            kmc = KMCOutput(
                path=sim_path,
                analysis_range=analysis_range,
                range_type=range_type,
                weights=weights,
            )
            kmc_ref = KMCOutput(
                path=ref_path,
                analysis_range=analysis_range,
                range_type=range_type,
                weights=weights,
            )

            tof = max(kmc.tof[gas_spec], 0.0)
            prod = kmc.total_production[gas_spec]
            tof_ref = max(kmc_ref.tof[gas_spec], 0.0)
            prod_ref = kmc_ref.total_production[gas_spec]

            # Store production for later use (even if we end up masking the point)
            df.loc[folder_name, "total_production"] = prod
            df.loc[folder_name, "total_production_ref"] = prod_ref

            has_main_issues = False
            has_ref_issues = False

            if check_issues in ['both', 'main']:
                has_main_issues = detect_issues(
                    job_path=sim_path,
                    analysis_range=analysis_range,
                    range_type=range_type,
                    energy_slope_thr=energy_slope_thr,
                    time_r2_thr=time_r2_thr,
                    max_points=max_points)

            if check_issues in ['both', 'ref']:
                has_ref_issues = detect_issues(
                    job_path=ref_path,
                    analysis_range=analysis_range,
                    range_type=range_type,
                    energy_slope_thr=energy_slope_thr,
                    time_r2_thr=time_r2_thr,
                    max_points=max_points)

            if check_issues == 'both':
                if has_main_issues or has_ref_issues:
                    df.loc[folder_name, "dtof"] = np.nan
                    continue
            elif check_issues == 'main':
                if has_main_issues:
                    df.loc[folder_name, "dtof"] = np.nan
                    continue
            elif check_issues == 'ref':
                if has_ref_issues:
                    df.loc[folder_name, "dtof"] = np.nan
                    continue

            # If a minimum reference TOF is requested, mask cells where the reference is below it
            if (min_tof_ref != 0.0) and (tof_ref < min_tof_ref):
                df.loc[folder_name, "dtof"] = np.nan
                continue

            # Only consider points above production threshold
            if prod >= min_molec and prod_ref >= min_molec:
                if difference_type == "absolute":
                    dtof_val = tof - tof_ref
                elif difference_type == "relative":
                    dtof_val = (abs(tof / tof_ref) if tof_ref != 0 else np.nan)
                else:
                    raise ValueError(
                        "difference_type must be 'absolute' or 'relative'"
                    )
            else:
                dtof_val = np.nan

            df.loc[folder_name, "dtof"] = dtof_val

        except Exception as e:
            print(f"Warning: could not process {folder_name}: {e}")
            df.loc[folder_name, ["dtof",
                                 "total_production",
                                 "total_production_ref"]] = np.nan

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
            dtof_val = df.loc[folder, "dtof"]

            if np.isnan(dtof_val):
                continue  # leave as NaN

            # Optional value capping (absolute vs relative handled later when N is known)
            if (difference_type == "absolute") and (max_dtof is not None):
                if dtof_val > max_dtof:
                    dtof_val = max_dtof
                elif dtof_val < -max_dtof:
                    dtof_val = -max_dtof

            z_axis[j, i] = dtof_val

    x_axis, y_axis = np.meshgrid(x_list, y_list)

    # --- Determine normalization parameters ---
    levels = None

    if difference_type == 'absolute':
        # Compute a symmetric maximum value from the grid.
        computed_abs_max = max(np.abs(np.nanmin(z_axis)), np.abs(np.nanmax(z_axis)))
        if max_dtof is None:
            exponent = np.ceil(np.log10(computed_abs_max)) if np.isfinite(computed_abs_max) and computed_abs_max > 0 else 0
            max_dtof = 10 ** exponent
        if min_dtof is None:
            min_dtof = max_dtof / 1.0e3
        abs_max = max_dtof

        # Normalization (continuous/discrete)
        if nlevels == 0:
            if scale == "lin":
                norm = Normalize(vmin=-abs_max, vmax=abs_max)
            elif scale == "log":
                if np.all(z_axis > 0):
                    norm = LogNorm(vmin=min_dtof, vmax=abs_max)
                elif np.all(z_axis < 0):
                    norm = LogNorm(vmin=-abs_max, vmax=-min_dtof)
                else:
                    norm = SymLogNorm(
                        linthresh=min_dtof,
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
                positive_levels = np.logspace(np.log10(min_dtof), np.log10(abs_max), (nlevels - 1) // 2)
                levels = np.concatenate((-positive_levels[::-1], [0], positive_levels))
            else:
                raise ValueError("scale parameter must be either 'log' or 'lin'")
            norm = colors.BoundaryNorm(levels, ncolors=plt.get_cmap(cmap).N, clip=True)

    else:
        # RELATIVE (ratio): force log scale centered at 10^0
        scale = 'log'

        # Determine data max (ratio) and choose nearest order of magnitude
        data_max = np.nanmax(z_axis)
        if not np.isfinite(data_max) or data_max <= 0:
            data_max = 1.0

        if max_dtof is None:
            N = int(np.round(np.log10(data_max)))
        else:
            N = int(np.round(np.log10(max_dtof)))
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
                raise ValueError("For relative mode, nlevels must be either 0 or an integer ≥ 2")
            levels = np.logspace(-abs(N), abs(N), nlevels)
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
            if difference_type == 'relative':
                def rel_log_formatter(x, pos):
                    # Show 10^{k}, centered at 10^0
                    if x <= 0 or not np.isfinite(x):
                        return ''
                    k = int(np.round(np.log10(x)))
                    # Only show pretty powers of ten; otherwise scientific
                    if np.isclose(x, 10 ** k, rtol=1e-5, atol=1e-12):
                        return r'$10^{%d}$' % k
                    return r'$%1.1e$' % x
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
            formatter = FuncFormatter(
                lambda x, pos: "0" if np.isclose(x, 0)
                else f"{x:+.0f}"
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
        _tag = "abs" if difference_type == "absolute" else "rel"
        label = f"$\\Delta\\mathrm{{TOF}}_{{{_tag}}}\\ {convert_to_subscript(gas_spec)}$"
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
