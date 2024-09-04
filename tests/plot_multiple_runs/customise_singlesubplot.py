import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

plot_heatmap(ax=axs, scan_path="./scan_results_POM_1000K_PtHfC", x="pressure_CH4", y="pressure_O2", z="tof",
             gas_spec="H2", window_percent=[50, 100], window_type="time", auto_title=True)

# Adjust size of axis ticks
axs.tick_params(axis='both', which='major', labelsize=12)

# Adjust fontsize of axis labels
axs.set_xlabel(axs.get_xlabel(), fontsize=16)
axs.set_ylabel(axs.get_ylabel(), fontsize=16)

# Adjust fontsize and position of axis title
axs.set_title(axs.get_title(), fontsize=20, loc='center', pad=-170)

plt.tight_layout()
plt.savefig('CustomiseSingle.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
