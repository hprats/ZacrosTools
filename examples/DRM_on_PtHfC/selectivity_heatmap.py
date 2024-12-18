import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

plot_heatmap(
    ax=axs,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
    z='selectivity',
    main_product='H2',
    side_products=['H2O'],
    min_molec=100,
    analysis_range=[50, 100],
    range_type='time',
    auto_title=True,
    show_points=False,
    show_colorbar=True
)

plt.tight_layout()
plt.savefig('selectivity_heatmap.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
