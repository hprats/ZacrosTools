import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

plot_heatmap(
    ax=axs,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
    z='energyslope',
    range_type='nevents',
    auto_title=True,
    show_points=False,
    show_colorbar=True
)

plt.tight_layout()
plt.savefig('energyslope_heatmap.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
