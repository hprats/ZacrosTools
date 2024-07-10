import numpy as np
import pandas as pd
from glob import glob
from zacrostools.kmc_output import KMCOutput
from zacrostools.read_functions import get_partial_pressures
from zacrostools.custom_exceptions import KMCOutputError
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe


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
        df.loc[folder_name, "total_production"] = kmc_output.total_production[product]
        df.loc[folder_name, "tof"] = kmc_output.tof[product]
        df.loc[folder_name, "log_pX"] = log_px
        df.loc[folder_name, "log_pY"] = log_py
        if log_px not in log_px_list:
            log_px_list.append(log_px)
        if log_py not in log_py_list:
            log_py_list.append(log_py)

    # Plot
    log_px_list = np.asarray(log_px_list)
    log_px_list = np.sort(log_px_list)
    log_py_list = np.asarray(log_py_list)
    log_py_list = np.sort(log_py_list)
    px_list = 10.0 ** log_px_list
    py_list = 10.0 ** log_py_list
    z = np.zeros((len(px_list), len(py_list)))
    x, y = np.meshgrid(px_list, py_list)

    for i, log_px in enumerate(log_px_list):
        for j, log_py in enumerate(log_py_list):
            if len(df[(df['log_pX'] == log_px) & (df['log_pY'] == log_py)].index) > 1:
                raise KMCOutputError(
                    f"several folders have the same values of log_p{reactants[0]} ({log_px}) and log_p{reactants[1]} ({log_py})")
            try:
                folder_name = df[(df['log_pX'] == log_px) & (df['log_pY'] == log_py)].index[0]
                if df.loc[folder_name, f"total_production"] > min_molec:
                    z[j, i] = np.log10(df.loc[folder_name, f"tof"])
                else:
                    z[j, i] = float('NaN')
            except IndexError:
                print(f"Warning: folder for pX = {px_list[i]} and pY = {py_list[j]} missing, NaN assigned")
                z[j, i] = float('NaN')
    cp = ax.contourf(x, y, z, levels=levels, cmap=cmap)
    plt.colorbar(cp, ax=ax)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_title(f"logTOF {product}", y=1.0, pad=-14, color="w",
                 path_effects=[pe.withStroke(linewidth=2, foreground="black")], fontsize=10)
    ax.set_facecolor("lightgray")
    return ax


def plot_coverage_scan():
    pass


def plot_selectivity_scan():
    pass


def plot_phase_diagram():
    pass
