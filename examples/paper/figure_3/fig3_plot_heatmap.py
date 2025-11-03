import numpy as np
import matplotlib.pyplot as plt
from zacrostools.heatmaps.tof import plot_tof
from zacrostools.heatmaps.coverage import plot_coverage
from zacrostools.heatmaps.phasediagram import plot_phasediagram
from zacrostools.heatmaps.selectivity import plot_selectivity
from zacrostools.heatmaps.finaltime import plot_finaltime
from zacrostools.heatmaps.dtof import plot_dtof

scan_path = '/Users/hprats/PycharmProjects/tmc4mpo/wp4/kmc/tests_Pt/temp_1100_DRM_1100K'
scan_path_ref = '/Users/hprats/PycharmProjects/tmc4mpo/wp4/kmc/tests_Pt/temp_1050_DRM_1050K'

# Plot parameters
x = 'pressure_CH4'
y = 'pressure_CO2'
analysis_range = [50, 100]
range_type = 'time'
weights = 'time'
auto_title = False
show_colorbar = True
min_molec = 10  # for TOF and selectivity plots

tick_labels = {  # for phase diagram plots
    '$CH_{x}$': ['CH3*', 'CH3_Pt*', 'CH2*', 'CH2_Pt*', 'CH*', 'CH_Pt*',
                 'C*', 'C_Pt*'],
    '$CHO/COH$': ['CHO*', 'CHO_Pt*', 'COH*', 'COH_Pt*'],
    '$CO$': ['CO*', 'CO_Pt*'],
    '$COOH$': ['COOH*', 'COOH_Pt*'],
    '$CO_{2}$': ['CO2*', 'CO2_Pt*'],
    '$H$': ['H*', 'H_Pt*'],
    '$H_{2}O$': ['H2O*', 'H2O_Pt*'],
    '$OH$': ['OH*', 'OH_Pt*'],
    '$O$': ['O*', 'O_Pt*']}

fig, axs = plt.subplots(4, 3, figsize=(9, 8), sharex='col', sharey='row')

for i, product in enumerate(['CO', 'H2', 'H2O']):
    plot_tof(
        ax=axs[0, i],
        x=x,
        y=y,
        scan_path=scan_path,
        gas_spec=product,
        min_molec=min_molec,
        weights=weights,
        levels=np.logspace(-1, 4, num=11),
        analysis_range=analysis_range,
        range_type=range_type,
        show_colorbar=show_colorbar,
        auto_title=auto_title
    )

for i, site_type in enumerate(['tC', 'tM', 'Pt']):
    plot_coverage(
        ax=axs[1, i],
        x=x,
        y=y,
        scan_path=scan_path,
        surf_spec='all',
        site_type=site_type,
        weights=weights,
        analysis_range=analysis_range,
        range_type=range_type,
        show_colorbar=show_colorbar,
        auto_title=auto_title
    )
    plot_phasediagram(
        ax=axs[2, i],
        x=x,
        y=y,
        scan_path=scan_path,
        site_type=site_type,
        min_coverage=50.0,
        tick_labels=tick_labels,
        weights=weights,
        analysis_range=analysis_range,
        range_type=range_type,
        show_colorbar=show_colorbar,
        auto_title=auto_title
    )

plot_selectivity(
    ax=axs[3, 0],
    x=x,
    y=y,
    scan_path=scan_path,
    main_product='H2',
    side_products=['H2O'],
    min_molec=min_molec,
    weights=weights,
    analysis_range=analysis_range,
    range_type=range_type,
    show_colorbar=show_colorbar,
    auto_title=auto_title
)

plot_finaltime(
    ax=axs[3, 1],
    x=x,
    y=y,
    scan_path=scan_path,
    levels=np.logspace(-5, 7, num=13),
    show_colorbar=show_colorbar,
    auto_title=auto_title
)

plot_dtof(
    ax=axs[3, 2],
    x=x,
    y=y,
    scan_path=scan_path,
    gas_spec='H2',
    scan_path_ref=scan_path_ref,
    difference_type='absolute',
    scale='log',
    min_molec=min_molec,
    weights=weights,
    analysis_range=analysis_range,
    range_type=range_type,
    show_colorbar=show_colorbar,
    auto_title=auto_title
)

nrows, ncols = axs.shape
for i in range(nrows):
    for j in range(ncols):
        if i < nrows - 1:  # Not the last row: remove x-labels
            axs[i, j].set_xlabel('')
        if j > 0:         # Not the first column: remove y-labels
            axs[i, j].set_ylabel('')

plt.tight_layout()
plt.subplots_adjust(hspace=0.3)
plt.savefig('/Users/hprats/Desktop/Figure_3.pdf', bbox_inches='tight', transparent=False, dpi=300)
plt.show()
