import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

plot_heatmap(ax=axs, scan_path="./scan_results_POM_1000K_PtHfC", scan_path_ref="./scan_results_POM_1000K_HfC",
             x="pressure_CH4", y="pressure_O2", z="tof_dif", min_molec=0,
             gas_spec="H2", window_percent=[50, 100], window_type="time")

axs.set_title("$log_{10}$∆TOF " + f"$H_{2}$", y=1.0, pad=-14, color="w",
              path_effects=[pe.withStroke(linewidth=2, foreground="black")], fontsize=10)

plt.tight_layout()
plt.savefig('ScanTofDif.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
