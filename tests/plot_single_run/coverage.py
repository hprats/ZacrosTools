import matplotlib.pyplot as plt
from zacrostools.kmc_output import KMCOutput


kmc_output = KMCOutput(path='./results_kmc', window_percent=[0, 100], window_type='time', weights='time')

plt.figure(figsize=(6, 4.5))
for site_type in kmc_output.site_types:
    for surf_species in kmc_output.coverage_per_site_type[site_type]:
        coverage = kmc_output.av_coverage_per_site_type[site_type][surf_species]
        if coverage >= 1.0:
            plt.plot(kmc_output.time, kmc_output.coverage_per_site_type[site_type][surf_species],
                     label=f"{surf_species} ({site_type})")

plt.xlabel('Simulated time (s)')
plt.ylabel('Surface coverage (%)')
plt.legend()
plt.tight_layout()
plt.savefig('Coverage.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
