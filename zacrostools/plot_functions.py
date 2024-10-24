import os
import numpy as np
import pandas as pd
from glob import glob
from zacrostools.kmc_output import KMCOutput, detect_issues
from zacrostools.read_functions import get_partial_pressures, parse_general_output, parse_simulation_input
from zacrostools.custom_exceptions import *
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import matplotlib.ticker as mticker
from matplotlib.colors import LogNorm


@enforce_types
def plot_heatmap(ax, scan_path: str, x: str, y: str, z: str,
                 gas_spec: str = None, scan_path_ref: str = None,
                 main_product: str = None, side_products: list = None,
                 surf_spec: Union[str, list] = None,
                 levels: Union[list, np.ndarray] = None, min_molec: int = 0,
                 site_type: str = 'default', min_coverage: Union[float, int] = 20.0,
                 surf_spec_values: dict = None, tick_values: list = None, tick_labels: list = None,
                 window_percent: list = None, window_type: str = 'time', verbose: bool = False,
                 weights: str = None, cmap: str = None, show_points: bool = False, show_colorbar: bool = True,
                 auto_title: bool = False):
    """
    Creates a contour or pcolormesh plot based on KMC simulation data.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axis object where the contour plot should be created.
    scan_path : str
        Path of the directory containing all the scan jobs.
    x : str
        Magnitude to plot on the x-axis ('pressure_X' or 'temperature').
    y : str
        Magnitude to plot on the y-axis ('pressure_Y' or 'temperature').
    z : str
        Magnitude to plot on the z-axis ('tof', 'tof_dif', 'selectivity', 'coverage', etc.).
    levels : list, optional
        Contour levels.
    min_molec : int, optional
        Minimum number of molecules required for TOF/selectivity plots.
    scan_path_ref : str, optional
        Path for reference scan jobs, required for 'tof_dif' plots.
    gas_spec : str, optional
        Gas species product for tof plots.
    surf_spec : str or list
        Surface species for coverage plots.
    main_product : str, optional
        Main product for selectivity plots.
    side_products : list, optional
        Side products for selectivity plots.
    site_type : str, optional
        Site type for coverage/phase diagrams. Default is 'default'.
    min_coverage : float, optional
        Minimum total coverage (%) to plot the dominant surface species on a phase diagram. Default is 20.0.
    surf_spec_values : dict, optional
        Surface species values for phase diagrams.
    tick_values : list, optional
        Tick values for phase diagram colorbar.
    tick_labels : list, optional
        Tick labels for phase diagram colorbar.
    window_percent : list, optional
        Window of the simulation to consider (percent). Default is [0, 100].
    window_type : str, optional
        Type of window to apply ('time' or 'nevents'). Default is 'time'.
    verbose : bool, optional
        If True, print paths of simulations with issues. Default is False.
    weights : str, optional
        Weights for averaging ('time', 'events', or None). Default is None.
    cmap : str, optional
        Colormap for the plot.
    show_points : bool, optional
        If True, show grid points as black dots. Default is False.
    show_colorbar : bool, optional
        If True, show the colorbar. Default is True.
    auto_title : bool, optional
        Automatically generates titles for subplots if True. Default is False.
    """

    if window_percent is None:
        window_percent = [30, 100] if z == "issues" else [0, 100]

    validate_params(z, gas_spec, scan_path, scan_path_ref, min_molec, main_product, side_products, surf_spec)

    # Initialize lists and DataFrame to store data
    log_x_list, log_y_list = [], []
    df = pd.DataFrame()

    # Parse all directories in scan_path and read x, y, and z values

    for simulation_path in glob(f"{scan_path}/*"):
        folder_name = simulation_path.split('/')[-1]
        if not os.path.isfile(f"{simulation_path}/general_output.txt"):
            print(f"Files not found: {folder_name}/general_output.txt")
            df.loc[folder_name, z] = float('NaN')
            continue

        # Read simulation output
        kmc_output, kmc_output_ref = initialize_kmc_outputs(simulation_path, z, scan_path_ref, folder_name,
                                                            window_percent, window_type, weights)

        # Read and store x and y values
        log_x = extract_log_value(x, simulation_path)
        log_y = extract_log_value(y, simulation_path)
        df.loc[folder_name, "log_x"] = log_x
        df.loc[folder_name, "log_y"] = log_y
        if log_x not in log_x_list:
            log_x_list.append(log_x)
        if log_y not in log_y_list:
            log_y_list.append(log_y)

        # Read and store z values
        if site_type == 'default':
            site_type = list(parse_general_output(simulation_path)['site_types'].keys())[0]
        df = process_z_value(z, df, folder_name, kmc_output, kmc_output_ref, gas_spec, surf_spec, main_product,
                             side_products, site_type, simulation_path, window_percent, verbose)

    # Handle plot default values
    if z in ["phase_diagram", "issues"]:
        surf_spec_values = surf_spec_values or {species: i + 0.5 for i, species in enumerate(
            sorted(parse_general_output(glob(f"{scan_path}/*")[0])['surf_species_names']))}

        tick_labels = {"phase_diagram": tick_labels or sorted(surf_spec_values.keys()),
                       "issues": tick_labels or ['Yes', 'No']}.get(z)
        tick_values = {"phase_diagram": tick_values or [n + 0.5 for n in range(len(surf_spec_values))],
                       "issues": tick_values or [-0.5, 0.5]}.get(z)

    if levels is not None:
        levels = list(levels)  # to convert possible numpy arrays into lists
    if z in ['selectivity', 'coverage', 'energy_slope']:
        levels = {
            "selectivity": levels or np.linspace(0, 100, 11, dtype=int),
            "coverage": levels or np.linspace(0, 100, 11, dtype=int),
            "energy_slope": levels or np.logspace(-11, -8, num=7)
        }.get(z)
        levels = list(levels)

    if cmap is None:
        cmap = {"tof": "inferno", "selectivity": "Greens", "coverage": "Oranges",
                "phase_diagram": "bwr", "final_time": "inferno", "final_energy": "inferno", "energy_slope": None,
                "issues": "RdYlGn"}.get(z)

    # Prepare plot data (z_axis)
    x_list, y_list, z_axis, z_axis_pos, z_axis_neg = prepare_plot_data(log_x_list, log_y_list, df, x, y, z, min_molec,
                                                                       min_coverage, surf_spec_values, levels)
    x_axis, y_axis = np.meshgrid(x_list, y_list)

    plot_types = {
        'contourf': ['tof', 'selectivity', 'coverage', 'final_time'],
        'pcolormesh': ['tof_dif', 'phase_diagram', 'energy_slope', 'issues']
    }
    z_data_in_log = ['tof', 'tof_dif', 'final_time', 'energy_slope']

    # Plot results
    cp, cp_neg, cp_pos = None, None, None

    if z in plot_types['contourf']:
        if z in z_data_in_log:
            cp = ax.contourf(x_axis, y_axis, z_axis, levels=levels if levels else None,
                             cmap=cmap, norm=LogNorm(vmin=min(levels), vmax=max(levels)) if levels else LogNorm())
        else:
            cp = ax.contourf(x_axis, y_axis, z_axis, levels=levels, cmap=cmap,
                             vmin=min(levels) if levels else None, vmax=max(levels) if levels else None)

    elif z in plot_types['pcolormesh']:
        if z == "tof_dif":
            vmin, vmax = (min(levels), max(levels)) if levels else (None, None)
            cp_neg = ax.pcolormesh(x_axis, y_axis, z_axis_neg, cmap="Reds", norm=LogNorm(vmin=vmin, vmax=vmax))
            cp_pos = ax.pcolormesh(x_axis, y_axis, z_axis_pos, cmap="Greens", norm=LogNorm(vmin=vmin, vmax=vmax))
        elif z == "phase_diagram":
            cp = ax.pcolormesh(x_axis, y_axis, z_axis, cmap=cmap, vmin=0, vmax=len(tick_labels))
        elif z == "energy_slope":
            vmin, vmax = (min(levels), max(levels)) if levels else (None, None)
            cp = ax.pcolormesh(x_axis, y_axis, z_axis, cmap=cmap, norm=LogNorm(vmin=vmin, vmax=vmax))
        elif z == "issues":
            cp = ax.pcolormesh(x_axis, y_axis, z_axis, cmap=cmap, vmin=-1, vmax=1)

    # Plot colorbar
    if show_colorbar:
        if z == "tof_dif":
            cbar_neg = plt.colorbar(cp_neg, ax=ax)
            cbar_pos = plt.colorbar(cp_pos, ax=ax)
        elif z == "phase_diagram":
            cbar = plt.colorbar(cp, ax=ax, ticks=tick_values, spacing='proportional',
                                boundaries=[n for n in range(len(tick_labels) + 1)],
                                format=mticker.FixedFormatter(tick_labels))
        elif z == "issues":
            cbar = plt.colorbar(cp, ax=ax, ticks=tick_values, spacing='proportional',
                                boundaries=[-1, 0, 1],
                                format=mticker.FixedFormatter(tick_labels))
        else:
            cbar = plt.colorbar(cp, ax=ax)

    ax.set_xlim(np.min(x_list), np.max(x_list))
    ax.set_ylim(np.min(y_list), np.max(y_list))

    # Set axis scales, labels and facecolor
    ax.set_xscale('log' if "pressure" in x else 'linear')
    ax.set_yscale('log' if "pressure" in y else 'linear')
    ax.set_xlabel(f"$p_{{{x.split('_')[-1]}}}$ (bar)" if "pressure" in x else "$T$ (K)")
    ax.set_ylabel(f"$p_{{{y.split('_')[-1]}}}$ (bar)" if "pressure" in y else "$T$ (K)")
    ax.set_facecolor("lightgray")

    if auto_title:
        title, pad = get_plot_title(z, gas_spec, main_product, site_type)
        ax.set_title(title, y=1.0, pad=pad, color="w", path_effects=[pe.withStroke(linewidth=2, foreground="black")])

    if show_points:
        for i in x_list:
            for j in y_list:
                ax.plot(i, j, marker='.', color='w', markersize=3)

    return cp


def validate_params(z, gas_spec, scan_path, scan_path_ref, min_molec, main_product, side_products, surf_spec):
    """ Validates the input parameters based on the z value. """

    if not os.path.isdir(scan_path):
        raise PlotError(f"Scan path folder does not exist: {scan_path}")

    if len(glob(f"{scan_path}/*")) == 0:
        raise PlotError(f"Scan path folder is empty: {scan_path}")

    allowed_z_values = ["tof", "tof_dif", "selectivity", "coverage", "phase_diagram", "final_time", "final_energy",
                        "energy_slope", "issues"]

    if z not in allowed_z_values:
        raise PlotError(f"Incorrect value for z: '{z}'. \nAllowed values are: {allowed_z_values}")

    if z == "tof" and not gas_spec:
        raise PlotError("'gas_spec' is required for 'tof' plots")

    elif z == "tof_dif":
        if not gas_spec or not scan_path_ref:
            raise PlotError("'gas_spec' and 'scan_path_ref' are required for 'tof_dif' plots")
        if not os.path.isdir(scan_path_ref):
            raise PlotError(f"{scan_path_ref}: 'scan_path_ref' directory does not exist")
        if min_molec != 0:
            print("Warning: 'min_molec' is ignored if z = 'tof_dif'")

    elif z == "selectivity" and (not main_product or not side_products):
        raise PlotError("'main_product' and 'side_products' are required for 'selectivity' plots")

    elif z == "coverage" and not surf_spec:
        raise PlotError("'scan_path_ref' is required for 'tof_dif' plots")


def initialize_kmc_outputs(path, z, scan_path_ref, folder_name, window_percent, window_type, weights):
    """ Initializes the KMCOutput objects for the main and reference paths. """
    kmc_output = None if z == 'issues' else KMCOutput(path=path, window_percent=window_percent,
                                                      window_type=window_type, weights=weights)
    kmc_output_ref = None
    if z == "tof_dif":
        kmc_output_ref = KMCOutput(path=f"{scan_path_ref}/{folder_name}", window_percent=window_percent,
                                   window_type=window_type, weights=weights)
    return kmc_output, kmc_output_ref


def extract_log_value(magnitude, path):
    """ Extracts the log10 value for a given magnitude from the simulation input. """
    if magnitude == 'temperature':
        temperature = parse_simulation_input(path)["temperature"]
        return round(np.log10(temperature), 8)
    elif "pressure" in magnitude:
        gas_species = magnitude.split('_')[-1]
        partial_pressures = get_partial_pressures(path)
        pressure = partial_pressures[gas_species]
        if pressure == 0:
            raise PlotError(f"Partial pressure of {gas_species} is zero in {path}")
        return round(np.log10(pressure), 8)
    else:
        raise PlotError(f"Incorrect value for {magnitude}")


def process_z_value(z, df, folder_name, kmc_output, kmc_output_ref, gas_spec, surf_spec, main_product, side_products,
                    site_type, simulation_path, window_percent, verbose):
    if z in ['tof', 'tof_dif']:
        df.loc[folder_name, "tof"] = kmc_output.tof[gas_spec]
        df.loc[folder_name, "total_production"] = kmc_output.total_production[gas_spec]

        if z == "tof_dif":
            df.loc[folder_name, "tof_ref"] = kmc_output_ref.tof[gas_spec]
            df.loc[folder_name, "total_production_ref"] = kmc_output_ref.total_production[gas_spec]

    elif z == "selectivity":
        df.loc[folder_name, "selectivity"] = kmc_output.get_selectivity(main_product=main_product,
                                                                        side_products=side_products)
        df.loc[folder_name, "main_and_side_prod"] = sum(
            kmc_output.total_production[prod] for prod in [main_product] + side_products)

    elif z == "coverage":
        df.loc[folder_name, "coverage"] = (kmc_output.av_total_coverage_per_site_type[site_type]
                                           if surf_spec == 'total' else
                                           sum(kmc_output.av_coverage_per_site_type[site_type].get(ads, 0.0)
                                               for ads in surf_spec))

    elif z == "phase_diagram":
        df.loc[folder_name, "dominant_ads"] = kmc_output.dominant_ads_per_site_type[site_type]
        df.loc[folder_name, "coverage"] = kmc_output.av_total_coverage_per_site_type[site_type]

    elif z in ['final_time', 'final_energy', 'energy_slope']:
        df.loc[folder_name, z] = getattr(kmc_output, z)

    elif z == 'issues':
        df.loc[folder_name, "issues"] = detect_issues(path=simulation_path, window_percent=window_percent)
        if df.loc[folder_name, "issues"] and verbose:
            print(f"Issue detected: {simulation_path}")

    return df


def get_plot_title(z, gas_spec, main_product, site_type):
    formated_gas_species = convert_to_subscript(chemical_formula=gas_spec) if z in ["tof", "tof_dif"] else ""
    formated_main_product = convert_to_subscript(chemical_formula=main_product) if z == "selectivity" else ""

    title = {"tof": "TOF " + f"${formated_gas_species}$",
             "tof_dif": "∆TOF " + f"${formated_gas_species}$",
             "selectivity": f"${formated_main_product}$ selectivity (%)",
             "coverage": f"coverage ${site_type}$",
             "phase_diagram": f"phase diagram ${site_type}$",
             "final_time": "final time ($s$)",
             "final_energy": "final energy ($eV·Å^{-2}$)",
             "energy_slope": "energy slope \n($eV·Å^{-2}·step^{-1}$)",
             "issues": "issues"}.get(z)

    pad = -28 if z == "energy_slope" else -14

    return title, pad


def prepare_plot_data(log_x_list, log_y_list, df, x, y, z, min_molec, min_coverage, surf_spec_values, levels):
    # Prepare data for plotting
    log_x_list = np.sort(np.asarray(log_x_list))
    log_y_list = np.sort(np.asarray(log_y_list))
    x_list = 10.0 ** log_x_list
    y_list = 10.0 ** log_y_list

    z_axis = np.full((len(x_list), len(y_list)), np.nan)
    z_axis_pos = np.full((len(x_list), len(y_list)), np.nan)
    z_axis_neg = np.full((len(x_list), len(y_list)), np.nan)

    for i, log_x in enumerate(log_x_list):
        for j, log_y in enumerate(log_y_list):

            if len(df[(df['log_x'] == log_x) & (df['log_y'] == log_y)].index) > 1:
                raise PlotError(
                    f"several folders have the same values of log_{x} ({log_x}) and log_{y} ({log_y})")

            elif len(df[(df['log_x'] == log_x) & (df['log_y'] == log_y)].index) == 0:
                print(f"Warning: folder for x = {x_list[i]} and y = {y_list[j]} missing, NaN assigned")

            else:
                folder_name = df[(df['log_x'] == log_x) & (df['log_y'] == log_y)].index[0]

                if z == "tof":
                    if levels:
                        z_val = max(df.loc[folder_name, "tof"], min(levels))
                    else:
                        z_val = max(df.loc[folder_name, "tof"], 1.0e-6)
                    if df.loc[folder_name, "total_production"] >= min_molec:
                        z_axis[j, i] = z_val

                elif z == "tof_dif":
                    tof_dif = df.loc[folder_name, "tof"] - df.loc[folder_name, "tof_ref"]
                    z_val = max(abs(tof_dif), 1.0e-06) if not levels else abs(tof_dif)
                    if tof_dif >= 0:
                        z_axis_pos[j, i] = z_val
                    else:
                        z_axis_neg[j, i] = z_val

                elif z == "selectivity":
                    if df.loc[folder_name, "main_and_side_prod"] >= min_molec:
                        z_axis[j, i] = df.loc[folder_name, "selectivity"]

                elif z == "phase_diagram" and df.loc[folder_name, "coverage"] > min_coverage:
                    z_axis[j, i] = surf_spec_values[df.loc[folder_name, "dominant_ads"]]

                elif z == 'issues' and not np.isnan(df.loc[folder_name, "issues"]):
                    z_axis[j, i] = -0.5 if df.loc[folder_name, "issues"] else 0.5

                elif z in {"coverage", "final_time", "final_energy", "energy_slope"}:
                    z_axis[j, i] = df.loc[folder_name, z]

    return x_list, y_list, z_axis, z_axis_pos, z_axis_neg


def convert_to_subscript(chemical_formula):
    result = ''
    for char in chemical_formula:
        if char.isnumeric():
            result += f"_{char}"
        else:
            result += char
    return result
