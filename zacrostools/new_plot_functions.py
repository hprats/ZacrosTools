import os
import numpy as np
import pandas as pd
from glob import glob
from zacrostools.kmc_output import KMCOutput, detect_issues
from zacrostools.read_functions import get_partial_pressures, parse_general_output, parse_simulation_input
from zacrostools.custom_exceptions import PlotError
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


def plot_contour(ax, scan_path: str, x: str, y: str, z: str,
                 levels: list = None, min_molec: int = 0,
                 scan_path_ref: str = None, main_product: str = None, side_products: list = None,
                 site_type: str = 'default', min_coverage: float = 20.0,
                 surf_spec_values: dict = None, tick_values: list = None, tick_labels: list = None,
                 window_percent: list = [0, 100], window_type: str = 'time', verbose: bool = False,
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
        Minimum coverage to plot in phase diagrams. Default is 20.0.
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

    def check_required_params():
        if "selectivity" in z:
            if not main_product or not side_products:
                raise PlotError("'main_product' and 'side_products' are required for selectivity plots")
        if "tof_difference" in z and not scan_path_ref:
            raise PlotError("'scan_path_ref' is required for tof difference plots")

    def get_log_values(partial_pressures, axis):
        if partial_pressures[axis.split('_')[-1]] == 0:
            raise PlotError(f"Partial pressure of {axis.split('_')[-1]} is zero")
        return np.log10(partial_pressures[axis.split('_')[-1]]) if "pressure" in axis else np.log10(
            parse_simulation_input(path)["temperature"])

    def read_simulation_data(path, folder_name):
        nonlocal log_x_list, log_y_list

        kmc_output = None if z == 'has_issues' else KMCOutput(path=path, window_percent=window_percent,
                                                              window_type=window_type, weights=weights)
        kmc_output_ref = KMCOutput(path=f"{scan_path_ref}/{folder_name}", window_percent=window_percent,
                                   window_type=window_type, weights=weights) if "tof_difference" in z else None

        partial_pressures = get_partial_pressures(path)
        log_x, log_y = get_log_values(partial_pressures, x), get_log_values(partial_pressures, y)

        df.at[folder_name, "log_x"], df.at[folder_name, "log_y"] = log_x, log_y
        log_x_list.add(log_x)
        log_y_list.add(log_y)

        z_data = {
            "tof": lambda: kmc_output.tof[z.split('_')[-1]],
            "tof_difference": lambda: abs(kmc_output.tof[z.split('_')[-1]] - kmc_output_ref.tof[z.split('_')[-1]]),
            "selectivity": lambda: kmc_output.get_selectivity(main_product, side_products),
            "coverage": lambda: kmc_output.av_coverage_per_site_type[site_type].get(z.split('_')[-1], np.nan),
            "coverage_total": lambda: kmc_output.av_total_coverage_per_site_type[site_type],
            "phase_diagram": lambda: (
            kmc_output.dominant_ads_per_site_type[site_type], kmc_output.av_total_coverage_per_site_type[site_type]),
            "final_time": lambda: kmc_output.final_time,
            "final_energy": lambda: kmc_output.final_energy,
            "energy_slope": lambda: kmc_output.energy_slope,
            "has_issues": lambda: detect_issues(path)
        }.get(z.split('_')[0], lambda: np.nan)()

        if z == "selectivity":
            df.at[folder_name, "main_and_side_prod"] = sum(
                [kmc_output.total_production[p] for p in [main_product] + side_products])
        if z == "tof_difference":
            z_data = np.log10(z_data) if df.at[folder_name, "tof"] > df.at[folder_name, "tof_ref"] else -np.log10(
                z_data)
        elif z == "tof":
            z_data = np.log10(max(z_data, 10 ** min(levels))) if min_molec == 0 or df.at[
                folder_name, "total_production"] > min_molec else np.nan
        elif z == "phase_diagram":
            z_data = surf_spec_values[df.at[folder_name, "dominant_ads"]] if df.at[
                                                                                 folder_name, "coverage"] > min_coverage else np.nan

        df.at[folder_name, z] = z_data

    def set_plot_defaults():
        if z == "phase_diagram":
            surf_spec_values = surf_spec_values or {species: i + 0.5 for i, species in enumerate(
                sorted(parse_general_output(glob(f"{scan_path}/*")[0])['surf_species_names']))}
            tick_labels = tick_labels or list(surf_spec_values.keys())
            tick_values = tick_values or [n + 0.5 for n in range(len(surf_spec_values))]

        cmap_dict = {
            "tof_difference": "RdYlGn", "has_issues": "RdYlGn",
            "tof": "inferno", "final_time": "inferno", "final_energy": "inferno", "energy_slope": "inferno",
            "selectivity": "Greens", "coverage": "Oranges", "phase_diagram": "bwr"
        }
        level_dict = {
            "tof_difference": [-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2],
            "tof": [-3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3],
            "selectivity": [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
            "final_time": [-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6],
            "energy_slope": [-12, -11.5, -11, -10.5, -10, -9.5, -9, -8.5, -8],
            "final_energy": [-0.4, -0.35, -0.3, -0.25, -0.2, -0.15, -0.1, -0.05, 0, 0.05, 0.1, 0.15, 0.2],
            "phase_diagram": tick_values
        }
        return cmap or cmap_dict.get(z, "viridis"), levels or level_dict.get(z, 20)

    def prepare_plot_data():
        check_required_params()
        folder_names = sorted(os.listdir(scan_path), key=lambda x: (len(x), x))
        global df, log_x_list, log_y_list
        df, log_x_list, log_y_list = pd.DataFrame(), set(), set()

        for folder_name in folder_names:
            if os.path.isdir(f"{scan_path}/{folder_name}"):
                try:
                    read_simulation_data(f"{scan_path}/{folder_name}", folder_name)
                except Exception as e:
                    print(f"Error processing {folder_name}: {str(e)}")

    def generate_contour_plot(cmap, levels):
        unique_log_x = sorted(log_x_list)
        unique_log_y = sorted(log_y_list)
        zz = np.full((len(unique_log_y), len(unique_log_x)), np.nan)

        for _, row in df.iterrows():
            zz[unique_log_y.index(row["log_y"]), unique_log_x.index(row["log_x"])] = row[z]

        if np.isnan(zz).all():
            raise PlotError(f"All z values are NaN for '{z}'. No plot can be created.")

        contour = ax.contourf(unique_log_x, unique_log_y, zz, cmap=cmap, levels=levels)
        if show_points:
            ax.plot(df['log_x'], df['log_y'], 'k.', markersize=5)
        if show_colorbar:
            cbar = plt.colorbar(contour, ax=ax)
            if z == "phase_diagram":
                cbar.set_ticks(tick_values)
                cbar.set_ticklabels(tick_labels)
        ax.set_xlabel(f"$\log_{{10}}(\ {x.split('_')[-1]} \ )$")
        ax.set_ylabel(f"$\log_{{10}}(\ {y.split('_')[-1]} \ )$")

    cmap, levels = set_plot_defaults()
    prepare_plot_data()
    generate_contour_plot(cmap, levels)

    return ax
