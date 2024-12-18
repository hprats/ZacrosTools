import numpy as np
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

# Plot parameters
scan_path = 'simulation_results'
x_variable = 'pressure_CH4'
y_variable = 'pressure_CO2'

analysis_range = [50, 100]  # (in %) Ignore first X% of total simulated time (equilibration)
range_type = 'time'
weights = 'time'

min_molec_tof = 0  # To plot TOF and selectivity
min_molec_selectivity = 100  # To plot TOF and selectivity
min_coverage = 50  # (in %) To plot phase diagrams

auto_title = True
show_points = False
show_colorbar = True

fig, axs = plt.subplots(4, 3, figsize=(8.8, 8), sharey='row', sharex='col')

for n, product in enumerate(['CO', 'H2', 'H2O']):
    plot_heatmap(
        ax=axs[0, n], scan_path=scan_path, x=x_variable, y=y_variable, z="tof",
        gas_spec=product, min_molec=min_molec_tof,
        analysis_range=analysis_range, range_type=range_type, levels=np.logspace(-1, 4, num=11),
        auto_title=auto_title, show_points=show_points, show_colorbar=show_colorbar)

for n, site_type in enumerate(['tC', 'tM', 'Pt']):
    plot_heatmap(
        ax=axs[1, n], scan_path=scan_path, x=x_variable, y=y_variable, z="coverage",
        surf_spec='all', site_type=site_type,
        analysis_range=analysis_range, range_type=range_type, weights=weights,
        auto_title=auto_title, show_points=show_points, show_colorbar=show_colorbar)

for n, site_type in enumerate(['tC', 'tM', 'Pt']):
    plot_heatmap(
        ax=axs[2, n], scan_path=scan_path, x=x_variable, y=y_variable, z="phasediagram",
        min_coverage=min_coverage, site_type=site_type,
        surf_spec_values={
            'CH3': 0.5, 'CH3_Pt': 0.5, 'CH2': 0.5, 'CH2_Pt': 0.5, 'CH': 0.5, 'CH_Pt': 0.5, 'C': 0.5,
            'C_Pt': 0.5,
            'CHO': 1.5, 'CHO_Pt': 1.5, 'COH': 1.5, 'COH_Pt': 1.5,
            'CO': 2.5, 'CO_Pt': 2.5,
            'COOH': 3.5, 'COOH_Pt': 3.5,
            'CO2': 4.5, 'CO2_Pt': 4.5,
            'H': 5.5, 'H_Pt': 5.5,
            'H2O': 6.5, 'H2O_Pt': 6.5,
            'OH': 7.5, 'OH_Pt': 7.5,
            'O': 8.5, 'O_Pt': 8.5
        },
        tick_values=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5],
        tick_labels=['$CH_{x}$', '$CHO/COH$', '$CO$', '$COOH$', '$CO_{2}$', '$H$', '$H_{2}O$', '$OH$', '$O$'],
        analysis_range=analysis_range, range_type=range_type, weights=weights,
        auto_title=auto_title, show_points=show_points, show_colorbar=show_colorbar)

plot_heatmap(
    ax=axs[3, 0], scan_path=scan_path, x=x_variable, y=y_variable, z='selectivity',
    main_product='H2', side_products=['H2O'], min_molec=min_molec_selectivity,
    analysis_range=analysis_range, range_type=range_type,
    auto_title=auto_title, show_points=show_points, show_colorbar=show_colorbar)

plot_heatmap(
    ax=axs[3, 1], scan_path=scan_path, x=x_variable, y=y_variable, z='finaltime',
    levels=np.logspace(-7, 7, num=15), auto_title=auto_title, show_points=show_points, show_colorbar=show_colorbar)

# Hide axis labels of intermediate subplots
for i in range(3):
    for j in range(3):
        axs[i, j].set_xlabel('')
for i in range(3):
    for j in range(1, 3):
        axs[i, j].set_ylabel('')

# Hide blank subplots
axs[3, 2].axis('off')

plt.tight_layout()
plt.savefig('multiple_heatmaps.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
