import os
import numpy as np
import pandas as pd
from glob import glob
from zacrostools.kmc_output import KMCOutput
from zacrostools.read_functions import get_partial_pressures, parse_general_output, parse_simulation_input
from zacrostools.custom_exceptions import *
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import matplotlib.ticker as mticker


@enforce_types
def plot_contour(
        # Mandatory arguments for all plots
        ax, scan_path: str, x: str, y: str, z: str,
        # Extra arguments for all plots except phase diagrams (optional)
        levels: Union[list, None] = None,
        # Extra arguments for tof and selectivity plots (optional)
        min_molec: int = 0,
        # Extra arguments for selectivity plots (required)
        main_product: Union[str, None] = None, side_products: Union[list, None] = None,
        # Extra arguments for coverage plots and phasediagram plots (optional)
        site_type: Union[str, None] = 'default',
        # Extra arguments for phasediagram plots (optional)
        min_coverage: Union[float, int] = 20.0, surf_spec_values: Union[dict, None] = None,
        tick_values: Union[list, None] = None, tick_labels: Union[list, None] = None,
        # Extra arguments for all plots except final time and final energy (optional)
        ignore: Union[float, int] = 0.0, weights: Union[str, None] = None,
        # Extra arguments for all plots (optional)
        cmap: Union[str, None] = None, show_points: bool = False, show_colorbar: bool = True):
    """
    Pass a figure object and return an updated figure with a contour plot on it .


    Parameters
    ----------
        ax: matplotlib.axes.Axes
            Axis object where the contour plot should be created.
        scan_path: str
            Path of the directory containing all the scan jobs.
        x: str
            Magnitude to plot in the x-axis. Possible values: 'pressure_X' (where X is a gas species) or 'temperature'.
        y: str
            Magnitude to plot in the y-axis. Possible values: 'pressure_Y' (where Y is a gas species) or 'temperature'.
        z: str
            Magnitude to plot in the z-axis. Possible values: 'tof_Z' (where Z is a gas species), 'selectivity',
            'coverage_Z' (where Z is a surface species), 'coverage_total', 'phase_diagram', 'final_time' or
            'final_energy'.
        levels: list, only for tof, selectivity and coverage plots (optional)
            Determines the number and positions of the contour lines / regions. Default: '[-3, -2.5, -2, -1.5, -1, -0.5,
             0, 0.5, 1, 1.5, 2, 2.5, 3]' for tof plots and '[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]' for
             selectivity plots.
        min_molec: int, only for tof and selectivity plots (optional)
            Defines a minimum number of product (if z = 'tof_Z') or main_product + side_products (if z = 'selectivity'
            molecules in order to calculate and plot either the tof or the selectivity. If the number of molecules is
            lower, the value of tof or selectivity at that point will be NaN. If min_molec=0, no threshold will be
            applied and any value of tof lower than min(levels) will be set to that value. Default: 0
        main_product: str, only for selectivity plots (required)
            Main product to calculate the selectivity.
        side_products: list, only for selectivity plots (required)
            List of side products to calculate the selectivity.
        site_type: str, only for coverage and phase diagrams (optional)
            Name of site type. For default lattice models or lattice models with only one site type site_type =
            'default' can be used. Default: 'default'.
        min_coverage: float, only for phase diagrams (optional)
            Minimum total coverage to plot the dominant surface species on a phase diagram. Default: 20.0.
        surf_spec_values: list, only for phase diagrams (optional)
            List of surface species to include in the phase diagram. If None, all surface species
            will be included. Default: None.
        tick_values: list, only for phase diagrams (optional)
            List of tick values for the colorbar in phase diagrams. If None, ticks are determined automatically from
            the input. Default: None.
        tick_labels: list, only for phase diagrams (optional)
        ignore: float (optional)
            Ignore first % of simulated time, i.e., equilibration (in %). Default value: 0.0.
        weights: str (optional)
            Weights for the averages. Possible values: 'time', 'events', None. If None, all weights are set to 1.
            Default value: None.
        cmap: str (optional)
            The Colormap or instance or registered colormap name used to map scalar data to colors.
        show_points: bool (optional)
            If True, show the grid points as black dots. Default value: False.
        show_colorbar: bool (optional)
            If True, show the colorbar. Default value: True.
    """

    """ Check if extra required attributes are provided """
    if "selectivity" in z:
        if main_product is None:
            raise PlotError("'main_product' is required for selectivity plots")
        if side_products is None:
            raise PlotError("'side_products' is required for selectivity plots")

    log_x_list = []
    log_y_list = []
    df = pd.DataFrame()
    for path in glob(f"{scan_path}/*"):
        folder_name = path.split('/')[-1]
        if os.path.isfile(f"{path}/general_output.txt"):
            kmc_output = KMCOutput(path=path, ignore=ignore, weights=weights)
            """ Read values for x and y """
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
                df.loc[folder_name, "total_production"] = kmc_output.total_production[z.split('_')[-1]]
                df.loc[folder_name, "tof"] = kmc_output.tof[z.split('_')[-1]]
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
            else:
                raise PlotError("Incorrect value for z")

        else:
            print(f"Files not found: {path}/general_output.txt")
            if "tof" in z:
                df.loc[folder_name, "total_production"] = 0
                df.loc[folder_name, "tof"] = float('NaN')
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
        if "tof" in z or z == "final_time" or z == "final_energy":
            cmap = "inferno"
        elif z == "selectivity":
            cmap = "Greens"
        elif "coverage" in z:
            cmap = "Oranges"
        elif z == "phase_diagram":
            cmap = "bwr"

    if levels is None:
        if "tof" in z:
            levels = [-3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3]
        elif z == "selectivity" or "coverage" in z:
            levels = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        elif z == "final_time":
            levels = [-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6]
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
                if "tof" in z:
                    if min_molec != 0:
                        if df.loc[folder_name, "total_production"] > min_molec:
                            z_axis[j, i] = np.log10(df.loc[folder_name, "tof"])
                        else:
                            z_axis[j, i] = float('NaN')
                    else:
                        z_axis[j, i] = np.log10(max(df.loc[folder_name, "tof"], 10**min(levels)))
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

    """ Choose type of plot """
    if z == "phase_diagram":
        cp = ax.pcolormesh(x_axis, y_axis, z_axis, cmap=cmap, vmin=0, vmax=len(tick_labels))
        if show_colorbar:
            cbar = plt.colorbar(cp, ax=ax, ticks=tick_values, spacing='proportional',
                                boundaries=[n for n in range(len(tick_labels) + 1)],
                                format=mticker.FixedFormatter(tick_labels))
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
    if "tof" in z:
        formated_gas_species = convert_to_subscript(chemical_formula=z.split('_')[-1])
        ax.set_title(f"logTOF ${formated_gas_species}$", y=1.0, pad=-14, color="w",
                     path_effects=[pe.withStroke(linewidth=2, foreground="black")], fontsize=10)
        ax.set_facecolor("lightgray")
    elif z == "selectivity":
        formated_main_product= convert_to_subscript(chemical_formula=main_product)
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

    if show_points:
        for i in x_list:
            for j in y_list:
                ax.plot(i, j, marker='.', color='w')

    return ax


def convert_to_subscript(chemical_formula):
    result = ''
    for char in chemical_formula:
        if char.isnumeric():
            result += f"_{char}"
        else:
            result += char
    return result
