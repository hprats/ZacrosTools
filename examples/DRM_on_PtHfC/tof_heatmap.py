import numpy as np
import matplotlib.pyplot as plt
from zacrostools.heatmaps.tof import plot_tof

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

plot_tof(
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
    show_colorbar=True
)

plt.tight_layout()
plt.savefig('tof_heatmap.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
