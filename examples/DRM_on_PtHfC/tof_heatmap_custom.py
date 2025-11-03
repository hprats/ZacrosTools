import numpy as np
import matplotlib.pyplot as plt
from zacrostools.heatmaps.tof import plot_tof

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

cp = plot_tof(
    ax=axs,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
    gas_spec='H2',
    min_molec=0,
    analysis_range=[50, 100],
    range_type='time',
    levels=np.logspace(-1, 4, num=11),
    auto_title=True,
    show_points=False,
    show_colorbar=False
)

# Adjust size of axis ticks
axs.tick_params(axis='both', which='major', labelsize=14)

# Adjust font size of axis labels
axs.set_xlabel(axs.get_xlabel(), fontsize=18)
axs.set_ylabel(axs.get_ylabel(), fontsize=18)

# Adjust font size and position of axis title
axs.set_title(axs.get_title(), fontsize=20, loc='center', pad=-170)

# Create colorbar and adjust the size of its tick labels
cbar = plt.colorbar(cp, ax=axs)
cbar.ax.tick_params(labelsize=14)  # Adjust the colorbar tick label size

plt.tight_layout()
plt.savefig('tof_heatmap_custom.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
