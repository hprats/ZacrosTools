import numpy as np
import pandas as pd
from glob import glob
from zacrostools.kmc_output import KMCOutput
from zacrostools.read_functions import get_partial_pressures, parse_general_output
from zacrostools.custom_exceptions import KMCOutputError
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import matplotlib.ticker as mticker


# todo: add weights? add default values


def plot_tof_scan(ax, scan_path, reactants, product, ignore, min_molec, levels, cmap):
    # Read data scan
    log_px_list = []
    log_py_list = []
    df = pd.DataFrame()
    for path in glob(f"{scan_path}/*"):
        folder_name = path.split('/')[-1]
        kmc_output = KMCOutput(path=path, ignore=ignore)
        partial_pressures = get_partial_pressures(f"{path}")
        log_px = round(np.log10(partial_pressures[reactants[0]]), 8)
        log_py = round(np.log10(partial_pressures[reactants[1]]), 8)
        df.loc[folder_name, "log_pX"] = log_px
        df.loc[folder_name, "log_pY"] = log_py
        df.loc[folder_name, "total_production"] = kmc_output.total_production[product]
        df.loc[folder_name, "tof"] = kmc_output.tof[product]
        if log_px not in log_px_list:
            log_px_list.append(log_px)
        if log_py not in log_py_list:
            log_py_list.append(log_py)

    # Plot
    log_px_list = np.sort(np.asarray(log_px_list))
    log_py_list = np.sort(np.asarray(log_py_list))
    px_list = 10.0 ** log_px_list
    py_list = 10.0 ** log_py_list
    z = np.zeros((len(px_list), len(py_list)))
    x, y = np.meshgrid(px_list, py_list)

    for i, log_px in enumerate(log_px_list):
        for j, log_py in enumerate(log_py_list):
            if len(df[(df['log_pX'] == log_px) & (df['log_pY'] == log_py)].index) > 1:
                raise KMCOutputError(
                    f"several folders have the same values of log_p{reactants[0]} ({log_px}) and log_p{reactants[1]} "
                    f"({log_py})")
            elif len(df[(df['log_pX'] == log_px) & (df['log_pY'] == log_py)].index) == 0:
                print(f"Warning: folder for pX = {px_list[i]} and pY = {py_list[j]} missing, NaN assigned")
                z[j, i] = float('NaN')
            else:
                folder_name = df[(df['log_pX'] == log_px) & (df['log_pY'] == log_py)].index[0]
                if df.loc[folder_name, "total_production"] > min_molec:
                    z[j, i] = np.log10(df.loc[folder_name, "tof"])
                else:
                    z[j, i] = float('NaN')
    cp = ax.contourf(x, y, z, levels=levels, cmap=cmap)
    plt.colorbar(cp, ax=ax)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_title(f"logTOF {product}", y=1.0, pad=-14, color="w",
                 path_effects=[pe.withStroke(linewidth=2, foreground="black")], fontsize=10)
    ax.set_facecolor("lightgray")
    return ax


def plot_selectivity_scan(ax, scan_path, reactants, main_product, side_products, ignore, min_molec, levels, cmap):
    # Read data scan
    log_px_list = []
    log_py_list = []
    df = pd.DataFrame()
    for path in glob(f"{scan_path}/*"):
        folder_name = path.split('/')[-1]
        kmc_output = KMCOutput(path=path, ignore=ignore)
        partial_pressures = get_partial_pressures(f"{path}")
        log_px = round(np.log10(partial_pressures[reactants[0]]), 8)
        log_py = round(np.log10(partial_pressures[reactants[1]]), 8)
        df.loc[folder_name, "log_pX"] = log_px
        df.loc[folder_name, "log_pY"] = log_py
        df.loc[folder_name, "selectivity"] = kmc_output.get_selectivity(main_product=main_product,
                                                                        side_products=side_products)
        df.loc[folder_name, "main_and_side_prod"] = kmc_output.total_production[main_product]
        for side_product in side_products:
            df.loc[folder_name, "main_and_side_prod"] += kmc_output.total_production[side_product]
        if log_px not in log_px_list:
            log_px_list.append(log_px)
        if log_py not in log_py_list:
            log_py_list.append(log_py)

    # Plot
    log_px_list = np.sort(np.asarray(log_px_list))
    log_py_list = np.sort(np.asarray(log_py_list))
    px_list = 10.0 ** log_px_list
    py_list = 10.0 ** log_py_list
    z = np.zeros((len(px_list), len(py_list)))
    x, y = np.meshgrid(px_list, py_list)

    for i, log_px in enumerate(log_px_list):
        for j, log_py in enumerate(log_py_list):
            if len(df[(df['log_pX'] == log_px) & (df['log_pY'] == log_py)].index) > 1:
                raise KMCOutputError(
                    f"several folders have the same values of log_p{reactants[0]} ({log_px}) and log_p{reactants[1]} "
                    f"({log_py})")
            elif len(df[(df['log_pX'] == log_px) & (df['log_pY'] == log_py)].index) == 0:
                print(f"Warning: folder for pX = {px_list[i]} and pY = {py_list[j]} missing, NaN assigned")
                z[j, i] = float('NaN')
            else:
                folder_name = df[(df['log_pX'] == log_px) & (df['log_pY'] == log_py)].index[0]
                if df.loc[folder_name, "main_and_side_prod"] > min_molec:
                    z[j, i] = df.loc[folder_name, "selectivity"]
                else:
                    z[j, i] = float('NaN')
    cp = ax.contourf(x, y, z, levels=levels, cmap=cmap)
    plt.colorbar(cp, ax=ax)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_title(f"{main_product} selectivity (%)", y=1.0, pad=-14, color="w",
                 path_effects=[pe.withStroke(linewidth=2, foreground="black")], fontsize=10)
    ax.set_facecolor("lightgray")
    return ax


def plot_coverage_scan(ax, scan_path, reactants, site_type, surf_spec, ignore, levels, cmap):
    # Read data scan
    log_px_list = []
    log_py_list = []
    df = pd.DataFrame()
    for path in glob(f"{scan_path}/*"):
        folder_name = path.split('/')[-1]
        kmc_output = KMCOutput(path=path, ignore=ignore)
        partial_pressures = get_partial_pressures(f"{path}")
        log_px = round(np.log10(partial_pressures[reactants[0]]), 8)
        log_py = round(np.log10(partial_pressures[reactants[1]]), 8)
        df.loc[folder_name, "log_pX"] = log_px
        df.loc[folder_name, "log_pY"] = log_py
        if site_type == 'default':
            site_type = list(parse_general_output(path)['site_types'].keys())[0]
        if surf_spec == 'total':
            df.loc[folder_name, "coverage"] = kmc_output.av_total_coverage_per_site_type[site_type]
        else:
            df.loc[folder_name, "coverage"] = kmc_output.av_coverage_per_site_type[site_type][surf_spec]
        if log_px not in log_px_list:
            log_px_list.append(log_px)
        if log_py not in log_py_list:
            log_py_list.append(log_py)

    # Plot
    log_px_list = np.sort(np.asarray(log_px_list))
    log_py_list = np.sort(np.asarray(log_py_list))
    px_list = 10.0 ** log_px_list
    py_list = 10.0 ** log_py_list
    z = np.zeros((len(px_list), len(py_list)))
    x, y = np.meshgrid(px_list, py_list)

    for i, log_px in enumerate(log_px_list):
        for j, log_py in enumerate(log_py_list):
            if len(df[(df['log_pX'] == log_px) & (df['log_pY'] == log_py)].index) > 1:
                raise KMCOutputError(
                    f"several folders have the same values of log_p{reactants[0]} ({log_px}) and log_p{reactants[1]} "
                    f"({log_py})")
            elif len(df[(df['log_pX'] == log_px) & (df['log_pY'] == log_py)].index) == 0:
                print(f"Warning: folder for pX = {px_list[i]} and pY = {py_list[j]} missing, NaN assigned")
                z[j, i] = float('NaN')
            else:
                folder_name = df[(df['log_pX'] == log_px) & (df['log_pY'] == log_py)].index[0]
                z[j, i] = df.loc[folder_name, "coverage"]
    cp = ax.contourf(x, y, z, levels=levels, cmap=cmap)
    plt.colorbar(cp, ax=ax)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_title(f"coverage_{site_type}", y=1.0, pad=-14, color="w",
                 path_effects=[pe.withStroke(linewidth=2, foreground="black")], fontsize=10)
    return ax


def plot_phase_diagram(ax, scan_path, reactants, site_type, min_coverage, ignore, cmap):
    # Read data scan
    log_px_list = []
    log_py_list = []
    df = pd.DataFrame()
    for path in glob(f"{scan_path}/*"):
        folder_name = path.split('/')[-1]
        kmc_output = KMCOutput(path=path, ignore=ignore)
        partial_pressures = get_partial_pressures(f"{path}")
        log_px = round(np.log10(partial_pressures[reactants[0]]), 8)
        log_py = round(np.log10(partial_pressures[reactants[1]]), 8)
        df.loc[folder_name, "log_pX"] = log_px
        df.loc[folder_name, "log_pY"] = log_py
        if site_type == 'default':
            site_type = list(parse_general_output(path)['site_types'].keys())[0]
        df.loc[folder_name, "dominant_ads"] = kmc_output.dominant_ads_per_site_type[site_type]
        df.loc[folder_name, "coverage"] = kmc_output.av_total_coverage_per_site_type[site_type]
        if log_px not in log_px_list:
            log_px_list.append(log_px)
        if log_py not in log_py_list:
            log_py_list.append(log_py)

    # Plot

    surf_species_names = parse_general_output(glob(f"{scan_path}/*")[0])['surf_species_names']
    ticks = [n + 0.5 for n in range(len(surf_species_names))]
    log_px_list = np.sort(np.asarray(log_px_list))
    log_py_list = np.sort(np.asarray(log_py_list))
    px_list = 10.0 ** log_px_list
    py_list = 10.0 ** log_py_list
    z = np.zeros((len(px_list), len(py_list)))
    x, y = np.meshgrid(px_list, py_list)

    for i, log_px in enumerate(log_px_list):
        for j, log_py in enumerate(log_py_list):
            if len(df[(df['log_pX'] == log_px) & (df['log_pY'] == log_py)].index) > 1:
                raise KMCOutputError(
                    f"several folders have the same values of log_p{reactants[0]} ({log_px}) and log_p{reactants[1]} "
                    f"({log_py})")
            elif len(df[(df['log_pX'] == log_px) & (df['log_pY'] == log_py)].index) == 0:
                print(f"Warning: folder for pX = {px_list[i]} and pY = {py_list[j]} missing, NaN assigned")
                z[j, i] = float('NaN')
            else:
                folder_name = df[(df['log_pX'] == log_px) & (df['log_pY'] == log_py)].index[0]
                if df.loc[folder_name, "coverage"] > min_coverage:
                    index = surf_species_names.index(df.loc[folder_name, "dominant_ads"])
                    z[j, i] = ticks[index]
    cp = ax.pcolormesh(x, y, z, cmap=cmap, vmin=0, vmax=len(surf_species_names))
    plt.colorbar(cp, ax=ax, ticks=[n + 0.5 for n in range(len(surf_species_names))], spacing='proportional',
                 boundaries=[n for n in range(len(surf_species_names))],
                 format=mticker.FixedFormatter(surf_species_names))
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_title(f"Phase diagram {site_type}", y=1.0, pad=-14, color="w",
                 path_effects=[pe.withStroke(linewidth=2, foreground="black")], fontsize=10)
    ax.set_facecolor("lightgray")
    return ax
