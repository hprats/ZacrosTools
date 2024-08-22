import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_contour

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

plot_contour(ax=axs, scan_path="./scan_results_POM_1000K_PtHfC", x="pressure_CH4", y="pressure_O2", z="has_issues",
             window_percent=[50, 100])

plt.tight_layout()
plt.savefig('ScanIssues.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
