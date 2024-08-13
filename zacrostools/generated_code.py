import os
import numpy as np
import pandas as pd
from glob import glob
from zacrostools.kmc_output import KMCOutput, detect_issues
from zacrostools.read_functions import get_partial_pressures, parse_general_output, parse_simulation_input
from zacrostools.custom_exceptions import PlotError
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import matplotlib.ticker as mticker


@enforce_types
def plot_contour(ax, scan_path: str, x: str, y: str, z: str,
                 gas_spec: str = None,
                 scan_path_ref: str = None,
                 main_product: str = None, side_products: list = None,
                 surf_spec: str = None,
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
    window_percent = window_percent or [0, 100]
    validate_params(z, gas_spec, scan_path_ref, main_product, side_products, surf_spec)

    log_x_list, log_y_list = set(), set()
    df = pd.DataFrame()

    for path in glob(f"{scan_path}/*"):
        folder_name = os.path.basename(path)
        if not os.path.isfile(f"{path}/general_output.txt"):
            handle_missing_files(df, folder_name, z)
            continue

        kmc_output, kmc_output_ref = initialize_kmc_outputs(path, z, scan_path_ref, folder_name, window_percent,
                                                            window_type, weights)

        log_x, log_y = extract_log_value(x, path), extract_log_value(y, path)
        df.loc[folder_name, ["log_x", "log_y"]] = [log_x, log_y]
        log_x_list.add(log_x)
        log_y_list.add(log_y)

        process_z_value(df, z, folder_name, kmc_output, kmc_output_ref, gas_spec, main_product, side_products,
                        surf_spec, site_type)

    surf_spec_values, tick_values, tick_labels, cmap, levels = handle_defaults(z, scan_path, surf_spec_values,
                                                                               tick_values, tick_labels, cmap, levels)

    x_list, y_list, z_axis = prepare_plot_data(log_x_list, log_y_list, df, x, y, z, levels, min_molec, min_coverage,
                                               surf_spec_values, verbose)

    cp = create_plot(ax, x_list, y_list, z_axis, z, cmap, levels, show_colorbar, tick_values, tick_labels)
    finalize_plot(ax, x_list, y_list, z, x, y, site_type, main_product, show_points, cp)

    return ax


def validate_params(z, product, scan_path_ref, main_product, side_products, surf_spec):
    if z == 'tof' and not product:
        raise PlotError("'product' is required for 'tof' plots")
    if z == 'tof_dif' and not (product and scan_path_ref):
        raise PlotError("'scan_path_ref' is required for 'tof_dif' plots")
    if z == "selectivity" and not (main_product and side_products):
        raise PlotError("'main_product' and 'side_products' are required for 'selectivity' plots")
    if z == "coverage" and not surf_spec:
        raise PlotError("'surf_spec' is required for 'coverage' plots")


def handle_missing_files(df, folder_name, z):
    print(f"Files not found: {folder_name}/general_output.txt")
    df.loc[folder_name, z] = np.nan
    if z == "tof":
        df.loc[folder_name, "total_production"] = 0
    if z == "selectivity":
        df.loc[folder_name, "main_and_side_prod"] = 0
    if z == "phase_diagram":
        df.loc[folder_name, "coverage"] = 0


def initialize_kmc_outputs(path, z, scan_path_ref, folder_name, window_percent, window_type, weights):
    kmc_output = None if z == 'has_issues' else KMCOutput(path, window_percent, window_type, weights)
    kmc_output_ref = KMCOutput(f"{scan_path_ref}/{folder_name}", window_percent, window_type,
                               weights) if z == "tof_dif" else None
    return kmc_output, kmc_output_ref


def extract_log_value(magnitude, path):
    value = None
    if magnitude == 'temperature':
        value = parse_simulation_input(path)["temperature"]
    elif "pressure" in magnitude:
        gas_species = magnitude.split('_')[-1]
        partial_pressures = get_partial_pressures(path)
        value = partial_pressures.get(gas_species, 0)
        if value == 0:
            raise PlotError(f"Partial pressure of {gas_species} is zero in {path}")
    else:
        raise PlotError(f"Incorrect value for {magnitude}")
    return round(np.log10(value), 8)


def process_z_value(df, z, folder_name, kmc_output, kmc_output_ref, gas_spec, main_product, side_products, surf_spec,
                    site_type):
    if z == 'tof':
        df.loc[folder_name, ["tof", "total_production"]] = [kmc_output.tof[gas_spec],
                                                            kmc_output.total_production[gas_spec]]
    elif z == "tof_dif":
        df.loc[folder_name, ["tof", "tof_ref"]] = [kmc_output.tof[gas_spec], kmc_output_ref.tof[gas_spec]]
    elif z == "selectivity":
        df.loc[folder_name, ["selectivity", "main_and_side_prod"]] = [
            kmc_output.get_selectivity(main_product, side_products),
            sum(kmc_output.total_production[prod] for prod in [main_product] + side_products)]
    elif z == "coverage":
        if site_type == 'default':
            site_type = list(parse_general_output(path)['site_types'].keys())[0]
        df.loc[folder_name, "coverage"] = kmc_output.av_total_coverage_per_site_type[
            site_type] if surf_spec == 'total' else kmc_output.av_coverage_per_site_type[site_type][surf_spec]
    elif z == "phase_diagram":
        if site_type == 'default':
            site_type = list(parse_general_output(path)['site_types'].keys())[0]
        df.loc[folder_name, ["dominant_ads", "coverage"]] = [kmc_output.dominant_ads_per_site_type[site_type],
                                                             kmc_output.av_total_coverage_per_site_type[site_type]]
    elif z == 'has_issues':
        df.loc[folder_name, "has_issues"] = detect_issues(path)


def handle_defaults(z, scan_path, surf_spec_values, tick_values, tick_labels, cmap, levels):
    if z == "phase_diagram":
        surf_spec_values = surf_spec_values or {species: i + 0.5 for i, species in enumerate(
            sorted(parse_general_output(glob(f"{scan_path}/*")[0])['surf_species_names']))}
        tick_labels = tick_labels or sorted(surf_spec_values.keys())
        tick_values = tick_values or [n + 0.5 for n in range(len(surf_spec_values))]
    if cmap is None:
        cmap = {"tof": "inferno", "tof_dif": "RdYlGn", "selectivity": "Greens", "coverage": "Oranges",
                "phase_diagram": "bwr", "has_issues": "RdYlGn"}.get(z)
    if levels is None:
        levels = {"tof": [-3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3],
                  "tof_dif": [-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2],
                  "selectivity": [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                  "coverage": [0, 5, 10, 15, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                  "phase_diagram": list(surf_spec_values.values()) + [list(surf_spec_values.values())[-1] + 1],
                  "has_issues": [-1, 0, 1]}.get(z)
    return surf_spec_values, tick_values, tick_labels, cmap, levels


def prepare_plot_data(log_x_list, log_y_list, df, x, y, z, levels, min_molec, min_coverage, surf_spec_values, verbose):
    x_list = sorted(log_x_list)
    y_list = sorted(log_y_list)
    z_axis = np.zeros((len(y_list), len(x_list)))

    for i, log_y in enumerate(y_list):
        for j, log_x in enumerate(x_list):
            folder_name = df.query(f"log_x == {log_x} and log_y == {log_y}").index[0]
            if z == "tof_dif":
                df.loc[folder_name, "tof_dif"] = np.log10(df.loc[folder_name, "tof"] / df.loc[folder_name, "tof_ref"])
            if z == "phase_diagram" and df.loc[folder_name, "coverage"] < min_coverage:
                df.loc[folder_name, "dominant_ads"] = "empty"
            if df.loc[folder_name, "total_production"] <= min_molec or df.loc[
                folder_name, "main_and_side_prod"] <= min_molec:
                z_axis[i, j] = np.nan
            else:
                z_axis[i, j] = df.loc[folder_name, z] if z != "phase_diagram" else surf_spec_values[
                    df.loc[folder_name, "dominant_ads"]]

    if verbose:
        print(f"Log {x}: {x_list}\nLog {y}: {y_list}\nLog {z}: {z_axis}")

    return x_list, y_list, z_axis


def create_plot(ax, x_list, y_list, z_axis, z, cmap, levels, show_colorbar, tick_values, tick_labels):
    cp = ax.contourf(x_list, y_list, z_axis, levels=levels, cmap=cmap,
                     extend='both') if z != "phase_diagram" else ax.pcolormesh(x_list, y_list, z_axis, cmap=cmap,
                                                                               shading='flat')

    if show_colorbar:
        cb = plt.colorbar(cp, ax=ax, ticks=tick_values, extend='both') if z == "phase_diagram" else plt.colorbar(cp,
                                                                                                                 ax=ax,
                                                                                                                 extend='both')
        if z == "phase_diagram":
            cb.ax.set_yticklabels(tick_labels)
    return cp


def finalize_plot(ax, x_list, y_list, z, x, y, site_type, main_product, show_points, cp):
    ax.set_xlabel(f"{x.capitalize().replace('_', ' ')}")
    ax.set_ylabel(f"{y.capitalize().replace('_', ' ')}")
    ax.set_title(
        f"{z.capitalize()}: {site_type.capitalize() if z == 'coverage' else main_product if z == 'selectivity' else ''}")

    ax.set_xticks(x_list)
    ax.set_yticks(y_list)
    ax.set_xticklabels([f"{tick:.2f}" for tick in np.log10(x_list)], rotation=45, ha="right")
    ax.set_yticklabels([f"{tick:.2f}" for tick in np.log10(y_list)])

    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda val, pos: f'{10 ** val:.0e}'))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda val, pos: f'{10 ** val:.0e}'))

    if show_points:
        ax.scatter(x_list, y_list, color='white', s=20, edgecolors='black')
    plt.show()
