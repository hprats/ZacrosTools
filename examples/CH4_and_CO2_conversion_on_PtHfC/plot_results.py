import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import matplotlib.ticker as mticker
from glob import glob
from zacrostools.kmc_output import KMCOutput

catalyst = 'PtHfC'  # PtHfC or HfC
reaction = 'DRM'  # DRM, SRM, POM, WGS or RWGS
scan_name = 'no_scaling'  # scaling_default or no_scaling
temperature = 1000
grid_points_pX = 15
grid_points_pY = 15
plot_points = []  # [2, 2] or []

ignore = 30  # (in %) Ignore first X% of total simulated time (equilibration)
min_molec = 20  # To plot TOF and selectivity
min_cov = 20  # (in %) To plot phase diagrams


print("\nPlotting results for scan ... ")
print(f"Catalyst: {catalyst}")
print(f"Reaction: {reaction}")
print(f"Temperature: {temperature} K")
print(f"Number of grid poits in pX: {grid_points_pX}")
print(f"Number of grid poits in pY: {grid_points_pY}")
print(f"Ignore first {ignore} % of total simulated time")
print(f"Plot TOF_X if molec_X produced > {min_molec} molecules")
print(f"Plot selectivity_X/Y if molec_X + molec_Y produced > {min_molec} molecules")
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

ignore = 50  # (in %) Ignore first X% of total simulated time (equilibration)
min_molec = 20  # To plot TOF and selectivity
min_cov = 20  # (in %) To plot phase diagrams

main_product = reactions[reaction]['main_product']
side_products = reactions[reaction]['side_products']
reactants = reactions[reaction]['reactants']
products = reactions[reaction]['products']

# Read data
df = pd.DataFrame()
scan_path = f"scan_{catalyst}_{reaction}_{temperature}K"
for path in glob(f"{scan_path}/*"):
    folder_name = path.split('/')[-1]
    kmc_output = KMCOutput(path=path, ignore=ignore, coverage_per_site=True, ads_sites=spec_sites)
    for product in products:
        df.loc[folder_name, f"production_{product}"] = kmc_output.production[product]
        df.loc[folder_name, f"tof_{product}"] = kmc_output.tof[product]
    df.loc[folder_name, f"selectivity"] = kmc_output.get_selectivity(main_product=main_product,
                                                                     side_products=side_products)
    df.loc[folder_name, "main_and_side_prod"] = kmc_output.production[main_product]
    for side_product in side_products:
        df.loc[folder_name, "main_and_side_prod"] += kmc_output.production[side_product]
    for i, site_type in enumerate(kmc_output.site_types):
        df.loc[folder_name, f"coverage_{site_type}"] = kmc_output.total_coverage_per_site_type[site_type]
        df.loc[folder_name, f"dominant_ads_{site_type}"] = kmc_output.dominant_ads_per_site_type[site_type]
    df.loc[folder_name, "final_time"] = kmc_output.final_time
    df.loc[folder_name, "final_energy"] = kmc_output.final_energy
    df.loc[folder_name, "area"] = kmc_output.area

df.to_csv(f"/Users/install/Desktop/{scan_name}.csv")

# Plot data
xlist = np.logspace(reactions[reaction]['logpX_min'], reactions[reaction]['logpX_min'] + 5, grid_points_pX)
ylist = np.logspace(reactions[reaction]['logpY_min'], reactions[reaction]['logpY_min'] + 5, grid_points_pY)
X, Y = np.meshgrid(xlist, ylist)
z = np.zeros((len(ylist), len(xlist)))
fig, axs = plt.subplots(3, 4, figsize=(11, 6.2), sharey='row', sharex='col')

labels = {'CO': '$CO$',
          'H2': '$H_{2}$',
          'H2O': '$H_{2}O$',
          'O2': '$O_{2}$',
          'CO2': '$CO_{2}$',
          'CH4': '$CH_{4}$'}

# TOF
for m, prod in enumerate(products):
    for i, pX in enumerate(xlist):
        for j, pY in enumerate(ylist):
            folder_name = f"{reactants[0]}_{pX:.3e}#{reactants[1]}_{pY:.3e}"
            if df.loc[folder_name, f"production_{prod}"] > min_molec:
                z[j, i] = np.log10(df.loc[folder_name, f"tof_{prod}"])
            else:
                z[j, i] = float('NaN')
    cp = axs[0, m].contourf(X, Y, z, levels=[-3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3], cmap='inferno')
    plt.colorbar(cp, ax=axs[0, m])
    axs[0, m].set_xscale('log')
    axs[0, m].set_yscale('log')
    axs[0, m].set_title(f"logTOF {labels[prod]}", y=1.0, pad=-14, color="w",
                        path_effects=[pe.withStroke(linewidth=2, foreground="black")], fontsize=10)
    axs[0, m].set_facecolor("lightgray")

# Total coverage
site_types = ['tC', 'tM']
for m, site_type in enumerate(site_types):
    for i, pX in enumerate(xlist):
        for j, pY in enumerate(ylist):
            folder_name = f"{reactants[0]}_{pX:.3e}#{reactants[1]}_{pY:.3e}"
            z[j, i] = df.loc[folder_name, f"coverage_{site_type}"]
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
            folder_name = f"{reactants[0]}_{pX:.3e}#{reactants[1]}_{pY:.3e}"
            coverage = df.loc[folder_name, f"coverage_{site_type}"]
            if coverage > min_cov:
                z[j, i] = spec_values[df.loc[folder_name, f"dominant_ads_{site_type}"]]
            else:
                z[j, i] = float('NaN')
    cp = axs[1, m + 2].contourf(X, Y, z, levels=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], cmap='bwr')
    plt.colorbar(cp, ax=axs[1, m + 2],
                 ticks=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5],
                 format=mticker.FixedFormatter(['$CH_{x}$', '$CHO$', '$CO$', '$COOH$', '$CO_{2}$', '$H$', '$H_{2}O$',
                                                '$OH$', '$O$']))

    axs[1, m + 2].set_xscale('log')
    axs[1, m + 2].set_yscale('log')
    axs[1, m + 2].set_title(f"Phase diagram {site_type}", y=1.0, pad=-14, color="w",
                            path_effects=[pe.withStroke(linewidth=2, foreground="black")], fontsize=10)
    axs[1, m + 2].set_facecolor("lightgray")

# Selectivity
for i, pX in enumerate(xlist):
    for j, pY in enumerate(ylist):
        folder_name = f"{reactants[0]}_{pX:.3e}#{reactants[1]}_{pY:.3e}"
        if df.loc[folder_name, "main_and_side_prod"] > min_molec:
            z[j, i] = df.loc[folder_name, "selectivity"]
        else:
            z[j, i] = float('NaN')
cp = axs[2, 0].contourf(X, Y, z, levels=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100], cmap='Greens')
plt.colorbar(cp, ax=axs[2, 0])
axs[2, 0].set_xscale('log')
axs[2, 0].set_yscale('log')
axs[2, 0].set_title(f"{labels[reactions[reaction]['main_product']]} selectivity (%)", y=1.0, pad=-14, color="w",
                    path_effects=[pe.withStroke(linewidth=2, foreground="black")], fontsize=10)
axs[2, 0].set_facecolor("lightgray")

# Final KMC time
for i, pX in enumerate(xlist):
    for j, pY in enumerate(ylist):
        folder_name = f"{reactants[0]}_{pX:.3e}#{reactants[1]}_{pY:.3e}"
        z[j, i] = np.log10(df.loc[folder_name, "final_time"])
cp = axs[2, 1].contourf(X, Y, z, levels=[-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5], cmap='inferno')
plt.colorbar(cp, ax=axs[2, 1])
axs[2, 1].set_xscale('log')
axs[2, 1].set_yscale('log')
axs[2, 1].set_title(f"Final time ($s$)", y=1.0, pad=-14, color="w",
                    path_effects=[pe.withStroke(linewidth=2, foreground="black")], fontsize=10)

# Final lattice energy
for i, pX in enumerate(xlist):
    for j, pY in enumerate(ylist):
        folder_name = f"{reactants[0]}_{pX:.3e}#{reactants[1]}_{pY:.3e}"
        z[j, i] = df.loc[folder_name, "final_energy"]
cp = axs[2, 2].contourf(X, Y, z, levels=[-0.4, -0.35, -0.3, -0.25, -0.2, -0.15, -0.1, -0.05, 0, 0.05, 0.1, 0.15, 0.2],
                        cmap='inferno')
plt.colorbar(cp, ax=axs[2, 2])
axs[2, 2].set_title("Final energy ($eV·Å^{-2}$)", y=1.0, pad=-14, color="w",
                    path_effects=[pe.withStroke(linewidth=2, foreground="black")], fontsize=10)

# Labels
for m in range(4):
    axs[2, m].set_xlabel('$p_{' + reactants[0] + '}$ (bar)')
for n in range(3):
    axs[n, 0].set_ylabel('$p_{' + reactants[1] + '}$ (bar)')

# Plot points
if plot_points:
    for pX in xlist:
        for pY in ylist:
            axs[plot_points[0], plot_points[1]].plot(pX, pY, marker='.', color='k')

plt.tight_layout()
plt.savefig(f'/Users/install/Desktop/Results_{scan_name}_{reaction}_{temperature}.pdf', bbox_inches='tight',
            transparent=False)

print(f"Figure saved: Results_{scan_name}_{reaction}_{temperature}.pdf")

plt.show()

