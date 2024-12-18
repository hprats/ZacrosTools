import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

plot_heatmap(
    ax=axs,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
    z='phase_diagram',
    min_coverage=50.0,
    site_type='tC',
    surf_spec_values={
        'CH3': 0.5, 'CH3_Pt': 0.5, 'CH2': 0.5, 'CH2_Pt': 0.5, 'CH': 0.5, 'CH_Pt': 0.5, 'C': 0.5,
        'C_Pt': 0.5,
        'CHO': 1.5, 'CHO_Pt': 1.5, 'COH': 1.5, 'COH_Pt': 1.5,
        'CO': 2.5, 'CO_Pt': 2.5,
        'COOH': 3.5, 'COOH_Pt': 3.5,
        'CO2': 4.5, 'CO2_Pt': 4.5,
        'H': 5.5, 'H_Pt': 5.5,
        'H2O': 6.5, 'H2O_Pt': 6.5,
        'OH': 7.5, 'OH_Pt': 7.5,
        'O': 8.5, 'O_Pt': 8.5
    },
    tick_values=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5],
    tick_labels=['$CH_{x}$', '$CHO/COH$', '$CO$', '$COOH$', '$CO_{2}$', '$H$', '$H_{2}O$', '$OH$', '$O$'],
    analysis_range=[50, 100],
    range_type='time',
    weights='time',
    auto_title=True,
    show_points=False,
    show_colorbar=True
)

plt.tight_layout()
plt.savefig('phasediagram_heatmap.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
