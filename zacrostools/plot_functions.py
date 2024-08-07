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
                 levels: list = None, min_molec: int = 0,
                 scan_path_ref: str = None, main_product: str = None, side_products: list = None,
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
        Magnitude to plot on the z-axis ('tof_Z', 'tof_difference_Z', 'selectivity', 'coverage_Z', etc.).
    levels : list, optional
        Contour levels.
    min_molec : int, optional
        Minimum number of molecules required for TOF/selectivity plots.
    scan_path_ref : str, optional
        Path for reference scan jobs, required for 'tof_difference' plots.
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
    """

    if window_percent is None:
        window_percent = [0, 100]

    if "selectivity" in z:
        if main_product is None:
            raise PlotError("'main_product' is required for selectivity plots")
        if side_products is None:
            raise PlotError("'side_products' is required for selectivity plots")

    if "tof_difference" in z:
        if scan_path_ref is None:
            raise PlotError("'scan_path_ref' is required for tof difference plots")

    log_x_list = []
    log_y_list = []
    df = pd.DataFrame()

    num_issues_detected = 0
    for path in glob(f"{scan_path}/*"):
        folder_name = path.split('/')[-1]

        if os.path.isfile(f"{path}/general_output.txt"):

            if z == 'has_issues':
                kmc_output = None
            else:
                kmc_output = KMCOutput(path=path, window_percent=window_percent, window_type=window_type,
                                       weights=weights)

            kmc_output_ref = None
            if "tof_difference" in z:
                kmc_output_ref = KMCOutput(path=f"{scan_path_ref}/{folder_name}", window_percent=window_percent,
                                           window_type=window_type, weights=weights)

            """ Read value for x"""

            partial_pressures = get_partial_pressures(f"{path}")
            if partial_pressures[x.split('_')[-1]] == 0:
                raise PlotError(f"partial pressure of {x.split('_')[-1]} is zero in {path}")
            if partial_pressures[y.split('_')[-1]] == 0:
                raise PlotError(f"partial pressure of {y.split('_')[-1]} is zero in {path}")
            if "pressure" in x:
                log_x = round(np.log10(partial_pressures[x.split('_')[-1]]), 8)
            elif x == 'temperature':
                temperature = parse_simulation_input(path)["temperature"]
                log_x = round(np.log10(temperature), 8)
            else:
                raise PlotError("Incorrect value for x")

            """ Read value for y"""

            if "pressure" in y:
                log_y = round(np.log10(partial_pressures[y.split('_')[-1]]), 8)
            elif y == 'temperature':
                temperature = parse_simulation_input(path)["temperature"]
                log_y = round(np.log10(temperature), 8)
            else:
                raise PlotError("Incorrect value for y")
            df.loc[folder_name, "log_x"] = log_x
            df.loc[folder_name, "log_y"] = log_y
            if log_x not in log_x_list:
                log_x_list.append(log_x)
            if log_y not in log_y_list:
                log_y_list.append(log_y)

            """ Read value for z """

            if "tof" in z:
                df.loc[folder_name, "tof"] = kmc_output.tof[z.split('_')[-1]]
                if "tof_difference" in z:
                    df.loc[folder_name, "tof_ref"] = kmc_output_ref.tof[z.split('_')[-1]]
                else:
                    df.loc[folder_name, "total_production"] = kmc_output.total_production[z.split('_')[-1]]

            elif z == "selectivity":
                df.loc[folder_name, "selectivity"] = kmc_output.get_selectivity(main_product=main_product,
                                                                                side_products=side_products)
                df.loc[folder_name, "main_and_side_prod"] = kmc_output.total_production[main_product]
                for side_product in side_products:
                    df.loc[folder_name, "main_and_side_prod"] += kmc_output.total_production[side_product]

            elif "coverage" in z:
                if site_type == 'default':
                    site_type = list(parse_general_output(path)['site_types'].keys())[0]
                if z.split('_')[-1] == 'total':
                    df.loc[folder_name, "coverage"] = kmc_output.av_total_coverage_per_site_type[site_type]
                else:
                    df.loc[folder_name, "coverage"] = kmc_output.av_coverage_per_site_type[site_type][z.split('_')[-1]]

            elif z == "phase_diagram":
                if site_type == 'default':
                    site_type = list(parse_general_output(path)['site_types'].keys())[0]
                df.loc[folder_name, "dominant_ads"] = kmc_output.dominant_ads_per_site_type[site_type]
                df.loc[folder_name, "coverage"] = kmc_output.av_total_coverage_per_site_type[site_type]

            elif z == 'final_time':
                df.loc[folder_name, "final_time"] = kmc_output.final_time

            elif z == 'final_energy':
                df.loc[folder_name, "final_energy"] = kmc_output.final_energy

            elif z == 'energy_slope':
                df.loc[folder_name, "energy_slope"] = kmc_output.energy_slope

            elif z == 'has_issues':
                df.loc[folder_name, "has_issues"] = detect_issues(path)
                if df.loc[folder_name, "has_issues"] and verbose:
                    num_issues_detected += 1
                    print(f"Issue {num_issues_detected} detected: {path}")

            else:
                raise PlotError("Incorrect value for z")

        else:
            print(f"Files not found: {path}/general_output.txt")

            if "tof" in z:
                df.loc[folder_name, "tof"] = float('NaN')
                if "tof_difference" in z:
                    df.loc[folder_name, "tof_ref"] = float('NaN')
                else:
                    df.loc[folder_name, "total_production"] = 0

            elif z == "selectivity":
                df.loc[folder_name, "selectivity"] = float('NaN')
                df.loc[folder_name, "main_and_side_prod"] = 0

            elif "coverage" in z:
                df.loc[folder_name, "coverage"] = float('NaN')

            elif z == "phase_diagram":
                df.loc[folder_name, "dominant_ads"] = float('NaN')
                df.loc[folder_name, "coverage"] = 0

            elif z == 'final_time':
                df.loc[folder_name, "final_time"] = float('NaN')

            elif z == 'final_energy':
                df.loc[folder_name, "final_energy"] = float('NaN')

            elif z == 'energy_slope':
                df.loc[folder_name, "energy_slope"] = float('NaN')

            elif z == 'has_issues':
                df.loc[folder_name, "has_issues"] = float('NaN')

    """ Set default values depending on the type of plot """

    if z == "phase_diagram":
        if surf_spec_values is None:
            surf_spec_names = sorted(parse_general_output(glob(f"{scan_path}/*")[0])['surf_species_names'])
            surf_spec_values = {species: i + 0.5 for i, species in enumerate(surf_spec_names)}
            if tick_labels is None:
                tick_labels = surf_spec_names
        if tick_values is None:
            tick_values = [n + 0.5 for n in range(len(surf_spec_values))]

    if cmap is None:
        if "tof_difference" in z or z == "has_issues":
            cmap = "RdYlGn"
        elif "tof" in z or z == "final_time" or z == "final_energy" or z == "energy_slope":
            cmap = "inferno"
        elif z == "selectivity":
            cmap = "Greens"
        elif "coverage" in z:
            cmap = "Oranges"
        elif z == "phase_diagram":
            cmap = "bwr"

    if levels is None:
        if "tof_difference" in z:
            levels = [-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2]
        elif "tof" in z:
            levels = [-3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3]
        elif z == "selectivity" or "coverage" in z:
            levels = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        elif z == "final_time":
            levels = [-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6]
        elif z == "energy_slope":
            levels = [-12, -11.5, -11, -10.5, -10, -9.5, -9, -8.5, -8]
        elif z == "final_energy":
            levels = [-0.4, -0.35, -0.3, -0.25, -0.2, -0.15, -0.1, -0.05, 0, 0.05, 0.1, 0.15, 0.2]

    """ Prepare arrays for contourf or pcolormesh plots """

    log_x_list = np.sort(np.asarray(log_x_list))
    log_y_list = np.sort(np.asarray(log_y_list))
    x_list = 10.0 ** log_x_list
    y_list = 10.0 ** log_y_list
    z_axis = np.zeros((len(x_list), len(y_list)))
    x_axis, y_axis = np.meshgrid(x_list, y_list)

    """ Plot data """

    for i, log_x in enumerate(log_x_list):
        for j, log_y in enumerate(log_y_list):

            if len(df[(df['log_x'] == log_x) & (df['log_y'] == log_y)].index) > 1:
                raise PlotError(
                    f"several folders have the same values of log_{x} ({log_x}) and log_{y} ({log_y})")

            elif len(df[(df['log_x'] == log_x) & (df['log_y'] == log_y)].index) == 0:
                print(f"Warning: folder for x = {x_list[i]} and y = {y_list[j]} missing, NaN assigned")
                z_axis[j, i] = float('NaN')

            else:
                folder_name = df[(df['log_x'] == log_x) & (df['log_y'] == log_y)].index[0]

                if "tof_difference" in z:
                    tof_difference = abs(df.loc[folder_name, "tof"] - df.loc[folder_name, "tof_ref"])
                    if df.loc[folder_name, "tof"] > df.loc[folder_name, "tof_ref"]:
                        z_axis[j, i] = np.log10(tof_difference)
                    else:
                        z_axis[j, i] = - np.log10(tof_difference)

                elif "tof" in z:
                    if min_molec != 0:
                        if df.loc[folder_name, "total_production"] > min_molec:
                            z_axis[j, i] = np.log10(df.loc[folder_name, "tof"])
                        else:
                            z_axis[j, i] = float('NaN')
                    else:
                        z_axis[j, i] = np.log10(max(df.loc[folder_name, "tof"], 10 ** min(levels)))

                elif z == "selectivity":
                    if df.loc[folder_name, "main_and_side_prod"] > min_molec:
                        z_axis[j, i] = df.loc[folder_name, "selectivity"]
                    else:
                        z_axis[j, i] = float('NaN')

                elif "coverage" in z:
                    z_axis[j, i] = df.loc[folder_name, "coverage"]

                elif z == "phase_diagram":
                    if df.loc[folder_name, "coverage"] > min_coverage:
                        z_axis[j, i] = surf_spec_values[df.loc[folder_name, "dominant_ads"]]
                    else:
                        z_axis[j, i] = float('NaN')

                elif z == 'final_time':
                    z_axis[j, i] = np.log10(df.loc[folder_name, "final_time"])

                elif z == 'final_energy':
                    z_axis[j, i] = df.loc[folder_name, "final_energy"]

                elif z == 'energy_slope':
                    z_axis[j, i] = np.log10(df.loc[folder_name, "energy_slope"])

                elif z == 'has_issues':
                    if np.isnan(df.loc[folder_name, "has_issues"]):
                        z_axis[j, i] = float('NaN')
                    elif df.loc[folder_name, "has_issues"]:
                        z_axis[j, i] = -0.5
                    else:
                        z_axis[j, i] = 0.5

    """ Choose type of plot """

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
    elif z == "energy_slope":
        cp = ax.pcolormesh(x_axis, y_axis, z_axis, cmap=cmap, vmin=-11, vmax=-8)
        if show_colorbar:
            cbar = plt.colorbar(cp, ax=ax)
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

    """ Update axis scales, titles and facecolor """

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

    if "tof_difference" in z:
        formated_gas_species = convert_to_subscript(chemical_formula=z.split('_')[-1])
        ax.set_title(f"log∆TOF ${formated_gas_species}$", y=1.0, pad=-14, color="w",
                     path_effects=[pe.withStroke(linewidth=2, foreground="black")], fontsize=10)
        ax.set_facecolor("lightgray")

    elif "tof" in z:
        formated_gas_species = convert_to_subscript(chemical_formula=z.split('_')[-1])
        ax.set_title(f"logTOF ${formated_gas_species}$", y=1.0, pad=-14, color="w",
                     path_effects=[pe.withStroke(linewidth=2, foreground="black")], fontsize=10)
        ax.set_facecolor("lightgray")

    elif z == "selectivity":
        formated_main_product = convert_to_subscript(chemical_formula=main_product)
        ax.set_title(f"${formated_main_product}$ selectivity (%)", y=1.0, pad=-14, color="w",
                     path_effects=[pe.withStroke(linewidth=2, foreground="black")], fontsize=10)
        ax.set_facecolor("lightgray")

    elif "coverage" in z:
        ax.set_title(f"coverage ${site_type}$", y=1.0, pad=-14, color="w",
                     path_effects=[pe.withStroke(linewidth=2, foreground="black")], fontsize=10)

    elif z == "phase_diagram":
        ax.set_title(f"phase diagram ${site_type}$", y=1.0, pad=-14, color="w",
                     path_effects=[pe.withStroke(linewidth=2, foreground="black")], fontsize=10)
        ax.set_facecolor("lightgray")

    elif z == "final_time":
        ax.set_title(f"final time ($s$)", y=1.0, pad=-14, color="w",
                     path_effects=[pe.withStroke(linewidth=2, foreground="black")], fontsize=10)

    elif z == "final_energy":
        ax.set_title("final energy ($eV·Å^{-2}$)", y=1.0, pad=-14, color="w",
                     path_effects=[pe.withStroke(linewidth=2, foreground="black")], fontsize=10)

    elif z == "energy_slope":
        ax.set_title("energy slope \n($eV·Å^{-2}·step^{-1}$)", y=1.0, pad=-28, color="w",
                     path_effects=[pe.withStroke(linewidth=2, foreground="black")], fontsize=10)

    elif z == "has_issues":
        ax.set_title("issues", y=1.0, pad=-14, color="w",
                     path_effects=[pe.withStroke(linewidth=2, foreground="black")], fontsize=10)
        ax.set_facecolor("lightgray")

    if show_points:
        for i in x_list:
            for j in y_list:
                ax.plot(i, j, marker='.', color='w', markersize=3)

    return ax


def convert_to_subscript(chemical_formula):
    result = ''
    for char in chemical_formula:
        if char.isnumeric():
            result += f"_{char}"
        else:
            result += char
    return result
