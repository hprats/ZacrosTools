import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, 3, figsize=(10, 2.8))

site_types = ['tC', 'tM', 'Pt']
for n, site_type in enumerate(site_types):
    plot_heatmap(ax=axs[n], scan_path="./scan_results_POM_1000K_PtHfC", x="pressure_CH4", y="pressure_O2", z="coverage",
                 surf_spec="total", site_type=site_type, window_percent=[50, 100], window_type="time")

plt.tight_layout()
plt.savefig('ScanCoverageTotal.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
