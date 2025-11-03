import numpy as np
import matplotlib.pyplot as plt
from zacrostools.heatmaps.finaltime import plot_finaltime

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))
plot_finaltime(
    ax=axs,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
    levels=np.logspace(-5, 7, num=13),
    auto_title=True,
    show_points=False,
    show_colorbar=True
)
plt.tight_layout()
plt.savefig('finaltime_heatmap.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
