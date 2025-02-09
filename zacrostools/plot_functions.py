import os
import numpy as np
import pandas as pd
from glob import glob
from typing import Union, Optional
from pathlib import Path
from zacrostools.kmc_output import KMCOutput
from zacrostools.detect_issues import detect_issues
from zacrostools.simulation_input import parse_simulation_input_file
from zacrostools.general_output import parse_general_output_file
from zacrostools.custom_exceptions import PlotError
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import matplotlib.ticker as mticker
from matplotlib.colors import LogNorm, SymLogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable


def plot_heatmap(
        ax,
        scan_path: str,
        x: str,
        y: str,
        z: str,
        gas_spec: str = None,
        scan_path_ref: str = None,
        main_product: str = None,
        side_products: list = None,
        surf_spec: Union[str, list] = None,
        levels: Optional[Union[list, np.ndarray]] = None,
        min_molec: int = 0,
        max_dtof: float = None,
        min_dtof: float = None,
        site_type: str = 'default',
        min_coverage: Union[float, int] = 50.0,
        surf_spec_values: dict = None,
        tick_values: list = None,
        tick_labels: list = None,
        analysis_range: list = None,
        range_type: str = 'time',
        verbose: bool = False,
        weights: str = None,
        cmap: str = None,
        show_points: bool = False,
        show_colorbar: bool = True,
        auto_title: bool = False,
        show_max: bool = False):
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
        Magnitude to plot on the z-axis ('tof', 'dtof', 'selectivity', 'coverage', etc.).
    gas_spec : str, optional
        Gas species product for tof plots.
    scan_path_ref : str, optional
        Path for reference scan jobs, required for 'dtof' plots.
    main_product : str, optional
        Main product for selectivity plots.
    side_products : list, optional
        Side products for selectivity plots.
    surf_spec : str or list
        Surface species for coverage plots. If 'all', the total coverage is computed.
    levels : list, optional
        Contour levels.
    min_molec : int, optional
        Minimum number of molecules required for TOF/selectivity plots.
    site_type : str, optional
        Site type for coverage/phase diagrams. Default is 'default'.
    min_coverage : float, optional
        Minimum total coverage (%) to plot the dominant surface species on a phase diagram. Default is 20.0.
    max_dtof : float, optional
        Maximum absolute value for TOF differences. If None, it is automatically determined.
    min_dtof : float, optional
        Minimum absolute value threshold for TOF differences. If None, it is set to max_dtof / 1.0e5.
    surf_spec_values : dict, optional
        Surface species values for phase diagrams.
    tick_values : list, optional
        Tick values for phase diagram colorbar.
    tick_labels : list, optional
        Tick labels for phase diagram colorbar.
    analysis_range : list, optional
        Portion of the entire simulation to consider for analysis. Default is `[0.0, 100.0]`.
    range_type : str, optional
        Determines the dimension used when applying `analysis_range`. Possible values are `'time'` and `'nevents'.
        Default is `'time'`.
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
    show_max : bool, optional
        If True and z = 'tof', display a golden '*' marker at the point with the highest TOF. Default is False.
    auto_title : bool, optional
        Automatically generates titles for subplots if True. Default is False.
    """

    if analysis_range is None:
        analysis_range = [30, 100] if z == "issues" else [0, 100]

    validate_params(z, gas_spec, scan_path, scan_path_ref, min_molec, main_product, side_products, surf_spec, show_max)

    # Determine if x and y are logarithmic based on their names
    x_is_log = True if "pressure" in x else False
    y_is_log = True if "pressure" in y else False

    # Initialize lists and DataFrame to store data
    x_value_list, y_value_list = [], []
    df = pd.DataFrame()

    # Parse all directories in scan_path and read x, y, and z values
    for simulation_path in glob(f"{scan_path}/*"):
        folder_name = os.path.basename(simulation_path)
        if not os.path.isfile(f"{simulation_path}/general_output.txt"):
            print(f"Files not found: {folder_name}/general_output.txt")
            df.loc[folder_name, z] = float('NaN')
            continue

        # Read simulation output
        kmc_output, kmc_output_ref = initialize_kmc_outputs(simulation_path, z, scan_path_ref, folder_name,
                                                            analysis_range, range_type, weights)

        # Read and store x and y values
        x_value = extract_value(x, simulation_path)
        y_value = extract_value(y, simulation_path)
        df.loc[folder_name, "x_value"] = x_value
        df.loc[folder_name, "y_value"] = y_value
        if x_value not in x_value_list:
            x_value_list.append(x_value)
        if y_value not in y_value_list:
            y_value_list.append(y_value)

        # Read and store z values
        if site_type == 'default':
            general_output = parse_general_output_file(output_file=f"{simulation_path}/general_output.txt")
            site_types = list(general_output['site_types'].keys())
            site_type = site_types[0]
        df = process_z_value(z, df, folder_name, kmc_output, kmc_output_ref, gas_spec, surf_spec, main_product,
                             side_products, site_type, simulation_path, analysis_range, verbose)

    # Handle plot default values
    if z in ["phasediagram", "issues"]:
        if surf_spec_values is None:
            if z == "phasediagram":
                input_files = glob(f"{scan_path}/*/simulation_input.dat")
                if not input_files:
                    raise PlotError("No 'simulation_input.dat' found in scan_path directories.")
                input_file = input_files[0]
                surf_specs_names = parse_simulation_input_file(input_file=input_file)['surf_specs_names']
                surf_spec_values = {species: i + 0.5 for i, species in enumerate(sorted(surf_specs_names))}
            else:
                surf_spec_values = {}
        if tick_labels is None:
            tick_labels = sorted(surf_spec_values.keys()) if z == "phasediagram" else ['Yes', 'No']
        if tick_values is None:
            if z == "phasediagram":
                tick_values = [n + 0.5 for n in range(len(surf_spec_values))]
            else:
                tick_values = [-0.5, 0.5]

    if levels is not None:
        levels = list(levels)  # to convert possible numpy arrays into lists
    if z in ['selectivity', 'coverage', 'energyslope']:
        if levels is None:
            levels = {
                "selectivity": np.linspace(0, 100, 11, dtype=int),
                "coverage": np.linspace(0, 100, 11, dtype=int),
                "energyslope": np.logspace(-11, -8, num=7)
            }[z]
        levels = list(levels)

    if cmap is None:
        cmap = {"tof": "inferno", "dtof": "RdYlBu", "selectivity": "Greens", "coverage": "Oranges",
                "phasediagram": "bwr", "finaltime": "inferno", "final_energy": "inferno", "energyslope": None,
                "issues": "RdYlGn"}.get(z)

    # Prepare plot data (z_axis)
    x_value_list = np.sort(np.asarray(x_value_list))
    y_value_list = np.sort(np.asarray(y_value_list))

    # For plotting, convert log values back to actual values if they were logged
    x_list = np.power(10, x_value_list) if x_is_log else x_value_list
    y_list = np.power(10, y_value_list) if y_is_log else y_value_list

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

                if z == "tof":
                    if levels:
                        z_val = max(df.loc[folder_name, "tof"], min(levels))
                    else:
                        z_val = max(df.loc[folder_name, "tof"], 1.0e-6)
                    if df.loc[folder_name, "total_production"] >= min_molec:
                        z_axis[j, i] = z_val

                elif z == "dtof":
                    dtof = df.loc[folder_name, "tof"] - df.loc[folder_name, "tof_ref"]
                    z_val = dtof
                    if df.loc[folder_name, "total_production"] >= min_molec:
                        z_axis[j, i] = z_val

                elif z == "selectivity":
                    if df.loc[folder_name, "main_and_side_prod"] >= min_molec:
                        z_axis[j, i] = df.loc[folder_name, "selectivity"]

                elif z == "phasediagram" and df.loc[folder_name, "coverage"] > min_coverage:
                    z_axis[j, i] = surf_spec_values[df.loc[folder_name, "dominant_ads"]]

                elif z == 'issues' and not np.isnan(df.loc[folder_name, "issues"]):
                    z_axis[j, i] = -0.5 if df.loc[folder_name, "issues"] else 0.5

                elif z in {"coverage", "finaltime", "final_energy", "energyslope"}:
                    z_axis[j, i] = df.loc[folder_name, z]

    x_axis, y_axis = np.meshgrid(x_list, y_list)

    plot_types = {
        'contourf': ['tof', 'selectivity', 'coverage', 'finaltime'],
        'pcolormesh': ['dtof', 'phasediagram', 'energyslope', 'issues']
    }
    z_data_in_log = ['tof', 'dtof', 'finaltime', 'energyslope']

    # Plot results
    cp, cbar = None, None

    if z in plot_types['contourf']:
        if z in z_data_in_log:
            cp = ax.contourf(x_axis, y_axis, z_axis, levels=levels if levels else None,
                             cmap=cmap, norm=LogNorm(vmin=min(levels), vmax=max(levels)) if levels else LogNorm())
        else:
            cp = ax.contourf(x_axis, y_axis, z_axis, levels=levels, cmap=cmap,
                             vmin=min(levels) if levels else None, vmax=max(levels) if levels else None)

    elif z in plot_types['pcolormesh']:
        if z == "dtof":
            if max_dtof is None:
                # Compute the maximum absolute value of z_axis
                max_val = np.nanmax(np.abs(z_axis))
                exponent = np.ceil(np.log10(max_val))
                max_dtof = 10 ** exponent  # Round up to nearest power of 10

            if min_dtof is None:
                min_dtof = max_dtof / 1.0e4  # Set min_dtof

            # Ensure min_dtof is not greater than max_dtof
            min_dtof = min(min_dtof, max_dtof)

            abs_max = max_dtof

            # Handle cases where all data might be positive or negative
            if np.all(z_axis >= 0):
                # All positive values
                norm = LogNorm(vmin=max(z_axis[z_axis > 0].min(), min_dtof), vmax=abs_max)
            elif np.all(z_axis <= 0):
                # All negative values
                norm = LogNorm(vmin=min(z_axis[z_axis < 0].max(), -abs_max), vmax=-min_dtof)
            else:
                # Symmetric log normalization
                norm = SymLogNorm(linthresh=min_dtof, linscale=1.0, vmin=-abs_max, vmax=abs_max, base=10)

            cp = ax.pcolormesh(x_axis, y_axis, z_axis, cmap=cmap, norm=norm)

        elif z == "phasediagram":
            cp = ax.pcolormesh(x_axis, y_axis, z_axis, cmap=cmap, vmin=0, vmax=len(tick_labels))

        elif z == "energyslope":
            vmin, vmax = (min(levels), max(levels)) if levels else (None, None)
            cp = ax.pcolormesh(x_axis, y_axis, z_axis, cmap=cmap, norm=LogNorm(vmin=vmin, vmax=vmax))

        elif z == "issues":
            cp = ax.pcolormesh(x_axis, y_axis, z_axis, cmap=cmap, vmin=-1, vmax=1)

    # Plot the maximum TOF marker if show_max is True and z is 'tof'
    if show_max and z == 'tof':
        max_index = np.nanargmax(z_axis)
        max_j, max_i = np.unravel_index(max_index, z_axis.shape)
        max_x = x_axis[max_j, max_i]
        max_y = y_axis[max_j, max_i]
        ax.plot(max_x, max_y, marker='*', color='gold', markersize=5)

    # Plot colorbar
    if show_colorbar:
        if z == "phasediagram":
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
    ax.set_xscale('log' if x_is_log else 'linear')
    ax.set_yscale('log' if y_is_log else 'linear')
    ax.set_xlabel(get_axis_label(x))
    ax.set_ylabel(get_axis_label(y))
    ax.set_facecolor("lightgray")

    if auto_title:
        title, pad = get_plot_title(z, gas_spec, main_product, site_type)
        ax.set_title(title, y=1.0, pad=pad, color="w", path_effects=[pe.withStroke(linewidth=2, foreground="black")])

    if show_points:
        ax.plot(x_axis.flatten(), y_axis.flatten(), 'w.', markersize=3)

    return cp


def get_axis_label(magnitude):
    if magnitude == 'temperature':
        return "$T$ (K)"
    elif magnitude == 'total_pressure':
        return "$p_{\\mathrm{total}}$ (bar)"
    elif "pressure" in magnitude:
        gas_species = magnitude.split('_')[-1]
        formatted_gas_species = convert_to_subscript(gas_species)
        return f"$p_{{{formatted_gas_species}}}$ (bar)"
    else:
        return magnitude  # Default case


def validate_params(z, gas_spec, scan_path, scan_path_ref, min_molec, main_product, side_products, surf_spec, show_max):
    """ Validates the input parameters based on the z value. """

    if not os.path.isdir(scan_path):
        raise PlotError(f"Scan path folder does not exist: {scan_path}")

    if len(glob(f"{scan_path}/*")) == 0:
        raise PlotError(f"Scan path folder is empty: {scan_path}")

    allowed_z_values = ["tof", "dtof", "selectivity", "coverage", "phasediagram", "finaltime", "final_energy",
                        "energyslope", "issues"]

    if z not in allowed_z_values:
        raise PlotError(f"Incorrect value for z: '{z}'. \nAllowed values are: {allowed_z_values}")

    if show_max and z != 'tof':
        raise PlotError("'show_max' parameter is only valid when z = 'tof'")

    if z == 'tof':
        if not gas_spec:
            raise PlotError("'gas_spec' is required for 'tof' plots")

    elif z == 'dtof':
        if not gas_spec or not scan_path_ref:
            raise PlotError("'gas_spec' and 'scan_path_ref' are required for 'dtof' plots")
        if not os.path.isdir(scan_path_ref):
            raise PlotError(f"{scan_path_ref}: 'scan_path_ref' directory does not exist")
        if min_molec != 0:
            print("Warning: 'min_molec' is ignored if z = 'dtof'")

    elif z == 'selectivity':
        if not main_product or side_products is None:
            raise PlotError("'main_product' is required and 'side_products' must be provided (can be an empty list) "
                            "for 'selectivity' plots")

    elif z == 'coverage':
        if not surf_spec:
            raise PlotError("'surf_spec' is required for 'coverage' plots")


def initialize_kmc_outputs(path, z, scan_path_ref, folder_name, analysis_range, range_type, weights):
    """Initializes the KMCOutput objects for the main and reference paths, handling missing files gracefully."""
    kmc_output = None
    kmc_output_ref = None

    if z != 'issues':
        try:
            kmc_output = KMCOutput(path=path, analysis_range=analysis_range,
                                   range_type=range_type, weights=weights)
        except Exception as e:
            print(f"Warning: Could not initialize KMCOutput for {folder_name}: {e}")
            kmc_output = None

    if z == 'dtof':
        try:
            kmc_output_ref = KMCOutput(path=f"{scan_path_ref}/{folder_name}", analysis_range=analysis_range,
                                       range_type=range_type, weights=weights)
        except Exception as e:
            print(f"Warning: Could not initialize reference KMCOutput for {folder_name}: {e}")
            kmc_output_ref = None

    return kmc_output, kmc_output_ref


def extract_value(magnitude: str, path: str) -> float:
    """ Extracts the value for a given magnitude from the simulation input."""

    input_file_path = Path(path) / "simulation_input.dat"
    data = parse_simulation_input_file(input_file=input_file_path)

    if magnitude == 'temperature':
        temperature = data.get("temperature")
        if temperature is None:
            raise PlotError(f"Temperature not found in {input_file_path}")
        return temperature

    elif magnitude == 'total_pressure':
        total_pressure = data.get("pressure")
        if total_pressure is None:
            raise PlotError(f"Total pressure not found in {input_file_path}")
        if total_pressure <= 0:
            raise PlotError(f"Total pressure is zero or negative in {path}")
        log_total_pressure = np.log10(total_pressure)
        return round(log_total_pressure, 8)

    elif magnitude.startswith("pressure_"):
        gas_species = magnitude.split('_')[-1]
        total_pressure = data.get("pressure")
        if total_pressure is None:
            raise PlotError(f"Total pressure not found in {input_file_path}")
        if total_pressure <= 0:
            raise PlotError(f"Total pressure is zero or negative in {path}")

        gas_specs_names = data.get('gas_specs_names')
        gas_molar_fracs = data.get('gas_molar_fracs')

        if gas_specs_names is None or gas_molar_fracs is None:
            raise PlotError(f"Gas specifications or molar fractions missing in {input_file_path}")

        try:
            index = gas_specs_names.index(gas_species)
        except ValueError:
            raise PlotError(f"Gas species '{gas_species}' not found in {input_file_path}")

        molar_fraction = gas_molar_fracs[index]

        partial_pressure = total_pressure * molar_fraction
        if partial_pressure <= 0:
            raise PlotError(f"Partial pressure for {gas_species} is zero or negative in {path}")
        log_partial_pressure = np.log10(partial_pressure)
        return round(log_partial_pressure, 8)

    else:
        raise PlotError(f"Incorrect value for {magnitude}")


def process_z_value(z, df, folder_name, kmc_output, kmc_output_ref, gas_spec, surf_spec, main_product, side_products,
                    site_type, simulation_path, analysis_range, verbose):
    """Processes the z value for a given simulation, handling missing KMCOutput data."""
    if kmc_output is None and z != 'issues':
        df.loc[folder_name, z] = float('NaN')
        return df

    if z == 'dtof' and kmc_output_ref is None:
        df.loc[folder_name, z] = float('NaN')
        return df

    if z in ['tof', 'dtof']:
        df.loc[folder_name, "tof"] = kmc_output.tof[gas_spec]
        df.loc[folder_name, "total_production"] = kmc_output.total_production[gas_spec]

        if z == "dtof":
            df.loc[folder_name, "tof_ref"] = kmc_output_ref.tof[gas_spec]
            df.loc[folder_name, "total_production_ref"] = kmc_output_ref.total_production[gas_spec]

    elif z == "selectivity":
        df.loc[folder_name, "selectivity"] = kmc_output.get_selectivity(main_product=main_product,
                                                                        side_products=side_products)
        df.loc[folder_name, "main_and_side_prod"] = sum(
            kmc_output.total_production[prod] for prod in [main_product] + side_products)

    elif z == "coverage":
        if surf_spec == 'all':
            df.loc[folder_name, "coverage"] = kmc_output.av_total_coverage_per_site_type[site_type]
        else:
            coverage = 0.0
            if isinstance(surf_spec, str):
                surf_spec = [surf_spec]
            for ads in surf_spec:
                coverage += kmc_output.av_coverage_per_site_type[site_type].get(ads, 0.0)
            df.loc[folder_name, "coverage"] = coverage

    elif z == "phasediagram":
        df.loc[folder_name, "dominant_ads"] = kmc_output.dominant_ads_per_site_type[site_type]
        df.loc[folder_name, "coverage"] = kmc_output.av_total_coverage_per_site_type[site_type]

    elif z in ['finaltime', 'final_energy', 'energyslope']:
        df.loc[folder_name, z] = getattr(kmc_output, z)

    elif z == 'issues':
        df.loc[folder_name, "issues"] = detect_issues(path=simulation_path, analysis_range=analysis_range)
        if df.loc[folder_name, "issues"] and verbose:
            print(f"Issue detected: {simulation_path}")

    return df


def get_plot_title(z, gas_spec, main_product, site_type):
    formated_gas_species = convert_to_subscript(chemical_formula=gas_spec) if z in ["tof", "dtof"] else ""
    formated_main_product = convert_to_subscript(chemical_formula=main_product) if z == "selectivity" else ""

    # Escape underscores in site_type
    formated_site_type = site_type.replace('_', r'\_')

    title = {
        "tof": "TOF " + f"${formated_gas_species}$",
        "dtof": "∆TOF " + f"${formated_gas_species}$",
        "selectivity": f"${formated_main_product}$ selectivity (%)",
        "coverage": f"coverage ${formated_site_type}$",
        "phasediagram": f"phase diagram ${formated_site_type}$",
        "finaltime": "final time ($s$)",
        "final_energy": "final energy ($eV·Å^{{-2}}$)",
        "energyslope": "energy slope \n($eV·Å^{{-2}}·step^{{-1}}$)",
        "issues": "issues"
    }.get(z)

    pad = -28 if z == "energyslope" else -14

    return title, pad


def convert_to_subscript(chemical_formula):
    result = ''
    for char in chemical_formula:
        if char.isnumeric():
            result += f"_{char}"
        else:
            result += char
    return result
