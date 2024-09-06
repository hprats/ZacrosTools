import numpy as np
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, figsize=(5, 3.5))

plot_heatmap(ax=axs, scan_path="./scan_results_POM_1000K_PtHfC", scan_path_ref="./scan_results_POM_1000K_HfC",
             x="pressure_CH4", y="pressure_O2", z="tof_dif",
             gas_spec="H2", window_percent=[50, 100], window_type="time", auto_title=True,
             levels=np.logspace(-3, 4, num=15))

plt.tight_layout()
plt.savefig('ScanTofDif.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
