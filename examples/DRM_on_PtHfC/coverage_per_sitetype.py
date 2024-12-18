import matplotlib.pyplot as plt
from zacrostools.kmc_output import KMCOutput

kmc_output = KMCOutput(
    path='simulation_results/CH4_3.728e-01#CO2_4.394e-01',
    analysis_range=[0, 100],
    range_type='time',
    weights='time')

fig, axs = plt.subplots(1, len(kmc_output.site_types),
                        figsize=(2.7 * len(kmc_output.site_types), 3), sharey='all')

for i, site_type in enumerate(kmc_output.site_types):
    for surf_spec_name in kmc_output.coverage_per_site_type[site_type]:
        av_coverage = kmc_output.av_coverage_per_site_type[site_type][surf_spec_name]
        if av_coverage >= 1.0:
            axs[i].plot(kmc_output.time, kmc_output.coverage_per_site_type[site_type][surf_spec_name],
                        label=surf_spec_name)
    axs[i].set_title(site_type)
    axs[i].legend()

axs[0].set_xlabel('Simulated time (s)')
axs[1].set_xlabel('Simulated time (s)')
axs[0].set_ylabel('Surface coverage (%)')

plt.tight_layout()
plt.savefig('coverage_per_sitetype.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()

