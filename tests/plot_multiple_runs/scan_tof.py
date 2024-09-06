import numpy as np
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

plot_heatmap(ax=axs, scan_path="./scan_results_POM_1000K_PtHfC", x="pressure_CH4", y="pressure_O2", z="tof",
             gas_spec="H2", window_percent=[50, 100], window_type="time", auto_title=True,
             levels=np.logspace(-3, 4, num=15), min_molec=0)

plt.tight_layout()
plt.savefig('ScanTof.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
