import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

scan_path = "./scan_results_POM_1000K_PtHfC"
x = "pressure_CH4"
y = "pressure_O2"
analysis_range = [50, 100]
range_type = "time"
min_molec = 10

surf_spec_values = {
    'CH3': 0.5, 'CH2': 0.5, 'CH': 0.5, 'C': 0.5, 'CH3_Pt': 0.5, 'CH2_Pt': 0.5, 'CH_Pt': 0.5, 'C_Pt': 0.5,
    'CHO': 1.5, 'CO': 2.5, 'CO_Pt': 2.5, 'COOH': 3.5, 'COOH_Pt': 3.5, 'CO2': 4.5, 'CO2_Pt': 4.5, 'H': 5.5,
    'H2O': 6.5, 'H2O_Pt': 6.5, 'OH': 7.5, 'OH_Pt': 7.5, 'O': 8.5, 'O_Pt': 8.5, 'O2_Pt': 8.5}
tick_values = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5]
tick_labels = ['$CH_{x}$', '$CHO$', '$CO$', '$COOH$', '$CO_{2}$', '$H$', '$H_{2}O$', '$OH$', '$O$']


fig, axs = plt.subplots(4, 4, figsize=(11, 9), sharey='row', sharex='col')

for n, product in enumerate(['CO', 'H2', 'H2O', 'CO2']):
    plot_heatmap(ax=axs[0, n], scan_path=scan_path, x=x, y=y, z="tof", gas_spec=product,
                 analysis_range=analysis_range, range_type=range_type, auto_title=True)

for n, site_type in enumerate(['tC', 'tM', 'Pt']):
    plot_heatmap(ax=axs[1, n], scan_path=scan_path, x=x, y=y, z="coverage", surf_spec="total",
                 analysis_range=analysis_range, range_type=range_type,
                 site_type=site_type, weights="time", auto_title=True)

for n, site_type in enumerate(['tC', 'tM', 'Pt']):
    plot_heatmap(ax=axs[2, n], scan_path=scan_path, x=x, y=y, z="phase_diagram",
                 analysis_range=analysis_range, range_type=range_type, site_type=site_type,
                 surf_spec_values=surf_spec_values, tick_values=tick_values, tick_labels=tick_labels,
                 min_coverage=20, weights="time", auto_title=True)

plot_heatmap(ax=axs[3, 0], scan_path=scan_path, x=x, y=y, z='selectivity', main_product="H2",
             side_products=["H2O"], analysis_range=analysis_range, range_type=range_type, min_molec=min_molec,
             auto_title=True)

plot_heatmap(ax=axs[3, 1], scan_path=scan_path, x=x, y=y, z='final_time', auto_title=True)

plot_heatmap(ax=axs[3, 2], scan_path=scan_path, x=x, y=y, z='energy_slope', analysis_range=analysis_range,
             range_type='nevents', auto_title=True)

plot_heatmap(ax=axs[3, 3], scan_path=scan_path, x=x, y=y, z='issues', analysis_range=analysis_range,
             auto_title=True)

# Hide empty axes:
axs[1, 3].axis('off')
axs[2, 3].axis('off')

plt.tight_layout()
plt.savefig('ScanMultipleTypes.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
