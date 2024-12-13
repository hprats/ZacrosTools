import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

cp = plot_heatmap(ax=axs, scan_path="./scan_results_POM_1000K_PtHfC", x="pressure_CH4", y="pressure_O2", z="tof",
                  gas_spec="H2", analysis_range=[50, 100], range_type="time", auto_title=True, show_colorbar=False)

# Create colorbar and adjust the size of its tick labels
cbar = plt.colorbar(cp, ax=axs)
cbar.ax.tick_params(labelsize=14)  # Adjust the colorbar tick label size

plt.tight_layout()
plt.savefig('CustomiseColorbar.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
