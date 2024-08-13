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


@enforce_types
def plot_contour(ax, scan_path: str, x: str, y: str, z: str,
                 # Mandatory for 'tof' and 'tof_dif'
                 gas_spec: str = None,
                 # Mandatory for 'tof_dif'
                 scan_path_ref: str = None,
                 # Mandatory for 'selectivity'
                 main_product: str = None, side_products: list = None,
                 # Mandatory for 'coverage'
                 surf_spec: str = None,
                 # Extra
                 levels: list = None, min_molec: int = 0,
                 site_type: str = 'default', min_coverage: float = 20.0,
                 surf_spec_values: dict = None, tick_values: list = None, tick_labels: list = None,
                 window_percent=None, window_type: str = 'time', verbose: bool = False,
                 weights: str = None, cmap: str = None, show_points: bool = False, show_colorbar: bool = True):
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
    """

    if window_percent is None:
        window_percent = [0, 100]

    validate_params(z, gas_spec, scan_path_ref, main_product, side_products, surf_spec)

    # Initialize lists and DataFrame to store data
    log_x_list, log_y_list = [], []
    df = pd.DataFrame()

    # Parse all directories in scan_path and read x, y, and z values
    for path in glob(f"{scan_path}/*"):
        folder_name = path.split('/')[-1]

        if not os.path.isfile(f"{path}/general_output.txt"):
            handle_missing_files(df, folder_name, z)
            continue

        kmc_output, kmc_output_ref = initialize_kmc_outputs(path, z, scan_path_ref, folder_name, window_percent,
                                                            window_type, weights)

        log_x = extract_log_value(x, path)
        log_y = extract_log_value(y, path)

        df.loc[folder_name, "log_x"] = log_x
        df.loc[folder_name, "log_y"] = log_y

        update_unique_values(log_x, log_y, log_x_list, log_y_list)

        # Extract z values based on the selected magnitude
        if z == 'tof':
            df.loc[folder_name, "tof"] = kmc_output.tof[gas_spec]
            df.loc[folder_name, "total_production"] = kmc_output.total_production[gas_spec]

        elif z == "tof_dif":
            df.loc[folder_name, "tof"] = kmc_output.tof[gas_spec]
            df.loc[folder_name, "tof_ref"] = kmc_output_ref.tof[gas_spec]

        elif z == "selectivity":
            df.loc[folder_name, "selectivity"] = kmc_output.get_selectivity(main_product=main_product,
                                                                            side_products=side_products)

            df.loc[folder_name, "main_and_side_prod"] = sum(kmc_output.total_production[prod]
                                                            for prod in [main_product] + side_products)

        elif z == "coverage":
            if site_type == 'default':
                site_type = list(parse_general_output(path)['site_types'].keys())[0]
            if surf_spec == 'total':
                df.loc[folder_name, "coverage"] = kmc_output.av_total_coverage_per_site_type[site_type]
            else:
                df.loc[folder_name, "coverage"] = kmc_output.av_coverage_per_site_type[site_type][surf_spec]

        elif z == "phase_diagram":
            if site_type == 'default':
                site_type = list(parse_general_output(path)['site_types'].keys())[0]
            df.loc[folder_name, "dominant_ads"] = kmc_output.dominant_ads_per_site_type[site_type]
            df.loc[folder_name, "coverage"] = kmc_output.av_total_coverage_per_site_type[site_type]

        elif z == 'has_issues':
            df.loc[folder_name, "has_issues"] = detect_issues(path)
            if df.loc[folder_name, "has_issues"] and verbose:
                print(f"Issue detected: {path}")

        else:
            raise PlotError("Incorrect value for z")

    # Handle phase diagram defaults
    if z == "phase_diagram":
        if surf_spec_values is None:
            surf_spec_names = sorted(parse_general_output(glob(f"{scan_path}/*")[0])['surf_species_names'])
            surf_spec_values = {species: i + 0.5 for i, species in enumerate(surf_spec_names)}
            if tick_labels is None:
                tick_labels = surf_spec_names
        if tick_values is None:
            tick_values = [n + 0.5 for n in range(len(surf_spec_values))]

    # Set default colormap
    if cmap is None:
        if z in ["tof_dif", "has_issues"]:
            cmap = "RdYlGn"
        elif z == "tof":
            cmap = "inferno"
        elif z == "selectivity":
            cmap = "Greens"
        elif z == "coverage":
            cmap = "Oranges"
        elif z == "phase_diagram":
            cmap = "bwr"

    # Set default levels
    if levels is None:
        if "tof" == z:
            levels = [-3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3]
        elif z == "tof_dif":
            levels = [-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2]
        elif z in ["selectivity", "coverage"]:
            levels = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

    # Prepare data for plotting
    log_x_list = np.sort(np.asarray(log_x_list))
    log_y_list = np.sort(np.asarray(log_y_list))
    x_list = 10.0 ** log_x_list
    y_list = 10.0 ** log_y_list
    z_axis = np.zeros((len(x_list), len(y_list)))
    x_axis, y_axis = np.meshgrid(x_list, y_list)

    for i, log_x in enumerate(log_x_list):
        for j, log_y in enumerate(log_y_list):

            z_axis[j, i] = float('NaN')

            if len(df[(df['log_x'] == log_x) & (df['log_y'] == log_y)].index) > 1:
                raise PlotError(
                    f"several folders have the same values of log_{x} ({log_x}) and log_{y} ({log_y})")

            elif len(df[(df['log_x'] == log_x) & (df['log_y'] == log_y)].index) == 0:
                print(f"Warning: folder for x = {x_list[i]} and y = {y_list[j]} missing, NaN assigned")

            else:
                folder_name = df[(df['log_x'] == log_x) & (df['log_y'] == log_y)].index[0]

                if z == "tof":
                    if min_molec != 0:
                        if df.loc[folder_name, "total_production"] > min_molec:
                            z_axis[j, i] = np.log10(df.loc[folder_name, "tof"])
                    else:
                        z_axis[j, i] = np.log10(max(df.loc[folder_name, "tof"], 10 ** min(levels)))

                elif z == "tof_dif":
                    tof_dif = abs(df.loc[folder_name, "tof"] - df.loc[folder_name, "tof_ref"])
                    if df.loc[folder_name, "tof"] > df.loc[folder_name, "tof_ref"]:
                        z_axis[j, i] = np.log10(tof_dif)
                    else:
                        z_axis[j, i] = - np.log10(tof_dif)

                elif z == "selectivity":
                    if df.loc[folder_name, "main_and_side_prod"] > min_molec:
                        z_axis[j, i] = df.loc[folder_name, "selectivity"]

                elif z == "coverage":
                    z_axis[j, i] = df.loc[folder_name, "coverage"]

                elif z == "phase_diagram":
                    if df.loc[folder_name, "coverage"] > min_coverage:
                        z_axis[j, i] = surf_spec_values[df.loc[folder_name, "dominant_ads"]]

                elif z == 'has_issues':
                    if not np.isnan(df.loc[folder_name, "has_issues"]):
                        if df.loc[folder_name, "has_issues"]:
                            z_axis[j, i] = -0.5
                        else:
                            z_axis[j, i] = 0.5

    # Plot using contour or pcolormesh
    if z == "phase_diagram":
        cp = ax.pcolormesh(x_axis, y_axis, z_axis, cmap=cmap, vmin=0, vmax=len(tick_labels))
        if show_colorbar:
            cbar = plt.colorbar(cp, ax=ax, ticks=tick_values, spacing='proportional',
                                boundaries=[n for n in range(len(tick_labels) + 1)],
                                format=mticker.FixedFormatter(tick_labels))
            for t in cbar.ax.get_yticklabels():
                t.set_fontsize(8)
    elif z == "has_issues":
        cp = ax.pcolormesh(x_axis, y_axis, z_axis, cmap=cmap, vmin=-1, vmax=1)
        if show_colorbar:
            cbar = plt.colorbar(cp, ax=ax, ticks=[-0.5, 0.5], spacing='proportional',
                                boundaries=[-1, 0, 1],
                                format=mticker.FixedFormatter(['Yes', 'No']))
            for t in cbar.ax.get_yticklabels():
                t.set_fontsize(8)
    else:
        cp = ax.contourf(x_axis, y_axis, z_axis, levels=levels, cmap=cmap)
        if show_colorbar:
            cbar = plt.colorbar(cp, ax=ax)
            for t in cbar.ax.get_yticklabels():
                t.set_fontsize(10)

    ax.set_xlim(np.min(x_list), np.max(x_list))
    ax.set_ylim(np.min(y_list), np.max(y_list))

    # Set axis scales
    if "pressure" in x:
        ax.set_xscale('log')
        ax.set_xlabel('$p_{' + x.split('_')[-1] + '}$ (bar)')
    else:
        ax.set_xlabel('$T$ (K)')
    if "pressure" in y:
        ax.set_yscale('log')
        ax.set_ylabel('$p_{' + y.split('_')[-1] + '}$ (bar)')
    else:
        ax.set_ylabel('$T$ (K)')

    # Set title
    pad = -14
    if z == "tof":
        formated_gas_species = convert_to_subscript(chemical_formula=z.split('_')[-1])
        title = "$log_{10}$TOF " + f"${formated_gas_species}$"

    if z == "tof_dif":
        formated_gas_species = convert_to_subscript(chemical_formula=z.split('_')[-1])
        title = "$log_{10}$∆TOF " + f"${formated_gas_species}$"

    elif z == "selectivity":
        formated_main_product = convert_to_subscript(chemical_formula=main_product)
        title = f"${formated_main_product}$ selectivity (%)"

    elif z == "coverage":
        title = f"coverage ${site_type}$"

    elif z == "phase_diagram":
        title = f"phase diagram ${site_type}$"

    elif z == "has_issues":
        title = "issues"

    else:
        title = ""

    ax.set_title(title, y=1.0, pad=pad, color="w",
                 path_effects=[pe.withStroke(linewidth=2, foreground="black")], fontsize=10)
    ax.set_facecolor("lightgray")

    if show_points:
        for i in x_list:
            for j in y_list:
                ax.plot(i, j, marker='.', color='w', markersize=3)

    return ax


def validate_params(z, product, scan_path_ref, main_product, side_products, surf_spec):
    """ Validates the input parameters based on the z value. """
    if z == 'tof' and not product:
        raise PlotError("'product' is required for 'tof' plots")

    elif z == 'tof_dif' and not product and not scan_path_ref:
        raise PlotError("'scan_path_ref' is required for 'tof_dif' plots")

    elif z == "selectivity" and (not main_product or not side_products):
        raise PlotError("'main_product' and 'side_products' are required for 'selectivity' plots")

    elif z == "coverage" and not surf_spec:
        raise PlotError("'scan_path_ref' is required for 'tof_dif' plots")


def handle_missing_files(df, folder_name, z):
    """ Handles the case where required files are missing in a path. """
    print(f"Files not found: {folder_name}/general_output.txt")
    df.loc[folder_name, z] = float('NaN')
    if z == "tof":
        df.loc[folder_name, "total_production"] = 0
    if z == "selectivity":
        df.loc[folder_name, "main_and_side_prod"] = 0
    if z == "phase_diagram":
        df.loc[folder_name, "coverage"] = 0


def initialize_kmc_outputs(path, z, scan_path_ref, folder_name, window_percent, window_type, weights):
    """ Initializes the KMCOutput objects for the main and reference paths. """
    kmc_output = None if z == 'has_issues' else KMCOutput(path=path, window_percent=window_percent,
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


def update_unique_values(log_x, log_y, log_x_list, log_y_list):
    """ Updates the unique x and y values lists. """
    if log_x not in log_x_list:
        log_x_list.append(log_x)
    if log_y not in log_y_list:
        log_y_list.append(log_y)


def convert_to_subscript(chemical_formula):
    result = ''
    for char in chemical_formula:
        if char.isnumeric():
            result += f"_{char}"
        else:
            result += char
    return result
