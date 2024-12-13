import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

plot_heatmap(ax=axs, scan_path="./scan_results_POM_1000K_PtHfC", x="pressure_CH4", y="pressure_O2",
             z="selectivity", main_product="H2", side_products=["H2O"], analysis_range=[50, 100], range_type="time",
             min_molec=10, auto_title=True)

plt.tight_layout()
plt.savefig('ScanSelectivity.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
