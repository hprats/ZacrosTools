import matplotlib.pyplot as plt
from zacrostools.heatmaps.coverage import plot_coverage

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))
plot_coverage(
    ax=axs,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
    surf_spec='all',
    site_type='tC',
    analysis_range=[50, 100],
    range_type='time',
    weights='time',
    auto_title=True,
    show_points=False,
    show_colorbar=True
)
plt.tight_layout()
plt.savefig('coverage_heatmap.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
