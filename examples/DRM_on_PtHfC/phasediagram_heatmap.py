import matplotlib.pyplot as plt
from zacrostools.heatmaps.phasediagram import plot_phasediagram

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

tick_labels = {  # for phase diagram plots
    '$CH_{x}$': ['CH3*', 'CH3_Pt*', 'CH2*', 'CH2_Pt*', 'CH*', 'CH_Pt*', 'C*', 'C_Pt*'],
    '$CHO/COH$': ['CHO*', 'CHO_Pt*', 'COH*', 'COH_Pt*'],
    '$CO$': ['CO*', 'CO_Pt*'],
    '$COOH$': ['COOH*', 'COOH_Pt*'],
    '$CO_{2}$': ['CO2*', 'CO2_Pt*'],
    '$H$': ['H*', 'H_Pt*'],
    '$H_{2}O$': ['H2O*', 'H2O_Pt*'],
    '$OH$': ['OH*', 'OH_Pt*'],
    '$O$': ['O*', 'O_Pt*'],
}


plot_phasediagram(
    ax=axs,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
    min_coverage=5.0,
    site_type='tC',
    tick_labels=tick_labels,
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
