import matplotlib.pyplot as plt
from zacrostools.kmc_output import KMCOutput


kmc_output = KMCOutput(path='./results_kmc', window_percent=[0, 100], window_type='time', weights='time')

fig, axs = plt.subplots(1, 2, figsize=(3 * len(kmc_output.site_types), 3), sharey='all')

for i, site_type in enumerate(kmc_output.site_types):
    for surf_species in kmc_output.coverage_per_site_type[site_type]:
        av_coverage = kmc_output.av_coverage_per_site_type[site_type][surf_species]
        if av_coverage >= 1.0:
            axs[i].plot(kmc_output.time, kmc_output.coverage_per_site_type[site_type][surf_species],
                        label=surf_species)
    axs[i].set_title(site_type)

axs[0].set_xlabel('Simulated time (s)')
axs[1].set_xlabel('Simulated time (s)')
axs[0].set_ylabel('Surface coverage (%)')
plt.legend()
plt.tight_layout()
plt.savefig('CoveragePerType.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
