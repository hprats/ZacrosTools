import numpy as np
import matplotlib.pyplot as plt
from zacrostools.heatmaps.tof import plot_tof
from zacrostools.heatmaps.dtof import plot_dtof
from zacrostools.heatmaps.selectivity import plot_selectivity
from zacrostools.heatmaps.coverage import plot_coverage
from zacrostools.heatmaps.phasediagram import plot_phasediagram
from zacrostools.heatmaps.finaltime import plot_finaltime

# Plot parameters
scan_path = 'simulation_results'
x_variable = 'pressure_CH4'
y_variable = 'pressure_CO2'

analysis_range = [50, 100]      # Ignore first 50 % of total simulated time (equilibration)
range_type = 'time'
weights = 'time'

min_molec_tof = 0               # For TOF and selectivity
min_molec_selectivity = 100     # For TOF and selectivity
min_coverage = 50               # (in %) To plot phase diagrams

auto_title = True
show_points = False
show_colorbar = True

# Define labels for phase diagram heatmaps
tick_labels = {
    '$CH_{x}$': ['CH3*', 'CH3_Pt*', 'CH2*', 'CH2_Pt*', 'CH*', 'CH_Pt*', 'C*', 'C_Pt*'],
    '$CHO/COH$': ['CHO*', 'CHO_Pt*', 'COH*', 'COH_Pt*'],
    '$CO$': ['CO*', 'CO_Pt*'],
    '$COOH$': ['COOH*', 'COOH_Pt*'],
    '$CO_{2}$': ['CO2*', 'CO2_Pt*'],
    '$H$': ['H*', 'H_Pt*'],
    '$H_{2}O$': ['H2O*', 'H2O_Pt*'],
    '$OH$': ['OH*', 'OH_Pt*'],
    '$O$': ['O*', 'O_Pt*'],
}

fig, axs = plt.subplots(4, 3, figsize=(8.8, 8), sharey='row', sharex='col')

for n, product in enumerate(['CO', 'H2', 'H2O']):
    plot_tof(
        ax=axs[0, n], scan_path=scan_path, x=x_variable, y=y_variable,
        gas_spec=product, min_molec=min_molec_tof,
        analysis_range=analysis_range, range_type=range_type, levels=np.logspace(-1, 4, num=11),
        auto_title=auto_title, show_points=show_points, show_colorbar=show_colorbar)

for n, site_type in enumerate(['tC', 'tM', 'Pt']):
    plot_coverage(
        ax=axs[1, n], scan_path=scan_path, x=x_variable, y=y_variable,
        surf_spec='all', site_type=site_type,
        analysis_range=analysis_range, range_type=range_type, weights=weights,
        auto_title=auto_title, show_points=show_points, show_colorbar=show_colorbar)

for n, site_type in enumerate(['tC', 'tM', 'Pt']):
    plot_phasediagram(
        ax=axs[2, n], scan_path=scan_path, x=x_variable, y=y_variable,
        min_coverage=min_coverage, site_type=site_type, tick_labels=tick_labels,
        analysis_range=analysis_range, range_type=range_type, weights=weights,
        auto_title=auto_title, show_points=show_points, show_colorbar=show_colorbar)

plot_selectivity(
    ax=axs[3, 0], scan_path=scan_path, x=x_variable, y=y_variable,
    main_product='H2', side_products=['H2O'], min_molec=min_molec_selectivity,
    analysis_range=analysis_range, range_type=range_type,
    auto_title=auto_title, show_points=show_points, show_colorbar=show_colorbar)

plot_finaltime(
    ax=axs[3, 1], scan_path=scan_path, x=x_variable, y=y_variable,
    levels=np.logspace(-7, 7, num=15), auto_title=auto_title, show_points=show_points, show_colorbar=show_colorbar)

plot_dtof(
    ax=axs[3, 2], scan_path=scan_path, x=x_variable, y=y_variable,
    scan_path_ref='simulation_results_reference', gas_spec='H2', min_molec=0, levels=np.logspace(-1, 4, num=11),
    analysis_range=analysis_range, range_type=range_type,
    auto_title=auto_title, show_points=show_points, show_colorbar=show_colorbar)

# Hide axis labels of intermediate subplots
for i in range(3):
    for j in range(3):
        axs[i, j].set_xlabel('')
for i in range(3):
    for j in range(1, 3):
        axs[i, j].set_ylabel('')

plt.tight_layout()
plt.savefig('multiple_heatmaps.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
