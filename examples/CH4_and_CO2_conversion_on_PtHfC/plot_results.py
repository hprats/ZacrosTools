import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import matplotlib.ticker as mticker
from zacrostools.analysis_functions import find_nearest
from zacrostools.read_functions import parse_general_output
from glob import glob

catalyst = 'PtHfC'  # PtHfC or HfC
reaction = 'DRM'  # DRM, SRM, POM, WGS or RWGS
temp = 1000  # in K
grid_points_pX = 15
grid_points_pY = 15
ignore = 30  # (in %) Ignore first 30% of total simulated time (equilibration)
min_tof = 1.0e-1  # (in molecules/s/Å2) Selectivity = NaN if TOF < min_tof
min_cov = 20  # (in %) Most dominant species = NaN if total coverage is < min_cov %

print("\nPlotting results for scan ... ")
print(f"Catalyst: {catalyst}")
print(f"Reaction: {reaction}")
print(f"Temperature: {temp} K")
print(f"Number of grid poits in pX: {grid_points_pX}")
print(f"Number of grid poits in pY: {grid_points_pY}")
print(f"Assume first {ignore} % of the simulated time is equilibration")
print(f"Calculate selectivity if TOF > {min_tof} molecules/s/Å2")
print(f"Plot most dominant species if total coverage is > {min_cov} %")
print(f"If any of these values is incorrect, change them in the script ... ")

reactions = {
    'DRM': {'reactants': ['CH4', 'CO2'], 'products': ['CO', 'H2', 'H2O', 'O2'], 'logpX_min': -3, 'logpY_min': -5,
            'main_product': 'H2', 'side_products': ['H2O']},
    'SRM': {'reactants': ['CH4', 'H2O'], 'products': ['CO', 'H2', 'CO2', 'O2'], 'logpX_min': -3, 'logpY_min': -6,
            'main_product': 'CO', 'side_products': ['CO2']},
    'POM': {'reactants': ['CH4', 'O2'], 'products': ['CO', 'H2', 'H2O', 'CO2'], 'logpX_min': -3, 'logpY_min': -8,
            'main_product': 'H2', 'side_products': ['H2O']},
    'WGS': {'reactants': ['CO', 'H2O'], 'products': ['CO2', 'H2', 'CH4', 'O2'], 'logpX_min': -3, 'logpY_min': -7,
            'main_product': 'CO2', 'side_products': ['CH4']},
    'RWGS': {'reactants': ['CO2', 'H2'], 'products': ['CO', 'H2O', 'CH4', 'O2'], 'logpX_min': -5, 'logpY_min': -4,
             'main_product': 'CO', 'side_products': ['CH4']}}

spec_sites = {
    # tC
    'CH3': 'tC', 'CH2': 'tC', 'CH': 'tC', 'C': 'tC', 'H': 'tC', 'O': 'tC', 'CO': 'tC', 'CO2': 'tC',
    'CHO': 'tC', 'COOH': 'tC',
    # tM
    'OH': 'tM', 'H2O': 'tM',
    # Pt/HfC
    'CH3_Pt': 'Pt', 'CH2_Pt': 'Pt', 'CH_Pt': 'Pt', 'C_Pt': 'Pt', 'O_Pt': 'Pt', 'OH_Pt': 'Pt', 'H2O_Pt': 'Pt',
    'CO_Pt': 'Pt', 'CO2_Pt': 'Pt', 'CHO_Pt': 'Pt', 'COOH_Pt': 'Pt',
}

prods = reactions[reaction]['products']

df = pd.DataFrame()
scan_path = f"scan_{catalyst}_{reaction}_{temp}K"
gen_out_data = parse_general_output(glob(f"{scan_path}/*")[0])
site_types = list(gen_out_data['site_types'])
for path in glob(f"{scan_path}/*"):
    folder_name = path.split('/')[-1]
    with open(f"{path}/specnum_output.txt", "r") as infile:
        header = infile.readline().split()
    full_data = np.loadtxt(f"{path}/specnum_output.txt", skiprows=1)
    try:
        # Remove equilibration data
        index = np.where(full_data[:, 2] == find_nearest(full_data[:, 2], full_data[-1, 2] * ignore / 100))[0][0]
        data = np.delete(full_data, slice(0, index), 0)
        # Get TOFs
        time = data[:, 2]
        for molecule in reactions[reaction]['products']:
            production = data[:, header.index(molecule)]
            df.loc[folder_name, f"tof{molecule}"] = np.polyfit(time, production, 1)[0] / gen_out_data['area']
        # Get selectivity
        production_main = data[:, header.index(reactions[reaction]['main_product'])]
        production_secondary = np.zeros(len(data))
        for molecule in reactions[reaction]['side_products']:
            production_secondary += data[:, header.index(molecule)]
        production_total = production_main + production_secondary
        tof_total = np.polyfit(time, production_total, 1)[0] / gen_out_data['area']
        if tof_total < min_tof:
            df.loc[folder_name, f"selectivity"] = float('NaN')
        else:
            tof_main = np.polyfit(time, production_main, 1)[0] / gen_out_data['area']
            df.loc[folder_name, f"selectivity"] = min(tof_main / tof_total * 100, 100)
        # Get total coverage and species with the highest coverage for each site
        for i, site_type in enumerate(site_types):
            num_specs = np.zeros(len(data))
            list_ads = [ads for ads, site in spec_sites.items() if site == site_type]
            dominant_ads = list_ads[0]
            for ads in list_ads:
                num_specs += data[:, header.index(f"{ads}*")]
                if np.average(data[:, header.index(f"{ads}*")]) > np.average(data[:, header.index(f"{dominant_ads}*")]):
                    dominant_ads = ads
            coverage = np.average(num_specs) / gen_out_data['site_types'][site_type] * 100
            df.loc[folder_name, f"Coverage {site_type} (%)"] = coverage
            df.loc[folder_name, f"Dominant ads {site_type}"] = dominant_ads
        df.loc[folder_name, f"KMC time"] = time[-1]
    except IndexError:
        print(f"Error reading {path}")
        print("Probably, the max KMC time was reached before taking the first snapshot")
        for molecule in reactions[reaction]['products']:
            df.loc[folder_name, f"tof{molecule}"] = float('NaN')
        df.loc[folder_name, f"selectivity"] = float('NaN')
        for i, site_type in enumerate(site_types):
            df.loc[folder_name, f"Coverage {site_type} (%)"] = float('NaN')
            df.loc[folder_name, f"Dominant ads {site_type}"] = float('NaN')

labels = {'CO': '$CO$',
          'H2': '$H_{2}$',
          'H2O': '$H_{2}O$',
          'O2': '$O_{2}$',
          'CO2': '$CO_{2}$',
          'CH4': '$CH_{4}$'}

xlist = np.logspace(reactions[reaction]['logpX_min'], reactions[reaction]['logpX_min'] + 5, grid_points_pX)
ylist = np.logspace(reactions[reaction]['logpY_min'], reactions[reaction]['logpY_min'] + 5, grid_points_pY)
X, Y = np.meshgrid(xlist, ylist)
z = np.zeros((len(ylist), len(xlist)))

fig1, axs = plt.subplots(3, 5, figsize=(13, 6.2), sharey='row', sharex='col')

# TOF
for m, prod in enumerate(prods):
    for i, pX in enumerate(xlist):
        for j, pY in enumerate(ylist):
            folder_name = f"{reactions[reaction]['reactants'][0]}_{pX:.3e}#{reactions[reaction]['reactants'][1]}_{pY:.3e}"
            z[j, i] = np.log10(max(df.loc[folder_name, f"tof{prod}"], min_tof))
    cp = axs[0, m].contourf(X, Y, z, levels=[-1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3], cmap='inferno')
    plt.colorbar(cp, ax=axs[0, m])
    axs[0, m].set_xscale('log')
    axs[0, m].set_yscale('log')
    axs[0, m].set_title(f"logTOF {labels[prod]}", y=1.0, pad=-14, color="w",
                        path_effects=[pe.withStroke(linewidth=2, foreground="black")], fontsize=10)

# Selectivity
for i, pX in enumerate(xlist):
    for j, pY in enumerate(ylist):
        folder_name = f"{reactions[reaction]['reactants'][0]}_{pX:.3e}#{reactions[reaction]['reactants'][1]}_{pY:.3e}"
        z[j, i] = df.loc[folder_name, "selectivity"]
cp = axs[0, -1].contourf(X, Y, z, levels=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100], cmap='Greens')
plt.colorbar(cp, ax=axs[0, -1])
axs[0, -1].set_xscale('log')
axs[0, -1].set_yscale('log')
axs[0, -1].set_title(f"{labels[reactions[reaction]['main_product']]} selectivity (%)", y=1.0, pad=-14, color="w",
                     path_effects=[pe.withStroke(linewidth=2, foreground="black")], fontsize=10)
axs[0, -1].set_facecolor("lightgray")

# Total coverage
if catalyst == 'HfC':
    site_types = ['tC', 'tM']
elif catalyst == 'PtHfC':
    site_types = ['tC', 'tM', 'Pt']
else:
    sys.exit('Invalid system')
for m, site_type in enumerate(site_types):
    for i, pX in enumerate(xlist):
        for j, pY in enumerate(ylist):
            folder_name = f"{reactions[reaction]['reactants'][0]}_{pX:.3e}#{reactions[reaction]['reactants'][1]}_{pY:.3e}"
            z[j, i] = df.loc[folder_name, f"Coverage {site_type} (%)"]
    cp = axs[1, m].contourf(X, Y, z, levels=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100], cmap='Oranges')
    plt.colorbar(cp, ax=axs[1, m])
    axs[1, m].set_xscale('log')
    axs[1, m].set_yscale('log')
    axs[1, m].set_title(f"Coverage {site_type}", y=1.0, pad=-14, color="w",
                        path_effects=[pe.withStroke(linewidth=2, foreground="black")], fontsize=10)

# Dominant species
spec_values = {
    'CH3': 0.5, 'CH2': 0.5, 'CH': 0.5, 'C': 0.5, 'H': 5.5, 'O': 8.5, 'CO': 2.5, 'CO2': 4.5, 'CHO': 1.5, 'COOH': 3.5,
    # tC
    'OH': 7.5, 'H2O': 6.5,  # tM
    'OH_in': 7.5, 'H2O_in': 6.5,  # in
    'CH3_Pt': 0.5, 'CH2_Pt': 0.5, 'CH_Pt': 0.5, 'C_Pt': 0.5, 'O_Pt': 8.5, 'OH_Pt': 7.5, 'H2O_Pt': 6.5, 'CO_Pt': 2.5,
    'CO2_Pt': 4.5, 'COOH_Pt': 3.5, 'O2_Pt': 8.5,  # Pt
}
for m, site_type in enumerate(site_types):
    for i, pX in enumerate(xlist):
        for j, pY in enumerate(ylist):
            folder_name = f"{reactions[reaction]['reactants'][0]}_{pX:.3e}#{reactions[reaction]['reactants'][1]}_{pY:.3e}"
            coverage = df.loc[folder_name, f"Coverage {site_type} (%)"]
            if coverage > min_cov:
                z[j, i] = spec_values[df.loc[folder_name, f"Dominant ads {site_type}"]]
            else:
                z[j, i] = float('NaN')
    cp = axs[2, m].contourf(X, Y, z, levels=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], cmap='bwr')
    plt.colorbar(cp, ax=axs[2, m],
                 ticks=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5],
                 format=mticker.FixedFormatter(['$CH_{x}$', '$CHO$', '$CO$', '$COOH$', '$CO_{2}$', '$H$', '$H_{2}O$',
                                                '$OH$', '$O$']))

    axs[2, m].set_xscale('log')
    axs[2, m].set_yscale('log')
    axs[2, m].set_title(f"Phase diagram {site_type}", y=1.0, pad=-14, color="w",
                        path_effects=[pe.withStroke(linewidth=2, foreground="black")],  fontsize=10)
    axs[2, m].set_facecolor("lightgray")

# Labels
for m in range(len(site_types), 5):
    axs[0, m].set_xlabel('$P_{' + reactions[reaction]['reactants'][0] + '}$ (bar)')
for m in range(5):
    axs[2, m].set_xlabel('$P_{' + reactions[reaction]['reactants'][0] + '}$ (bar)')
for n in range(3):
    axs[n, 0].set_ylabel('$P_{' + reactions[reaction]['reactants'][1] + '}$ (bar)')

for i in range(1, 3):
    for j in range(len(site_types), 5):
        axs[i, j].axis('off')

plt.tight_layout()
plt.savefig(f'Results_{reaction}_{catalyst}.pdf', bbox_inches='tight', transparent=False)

print(f"Figure saved: Results_{reaction}_{catalyst}.pdf")

plt.show()
