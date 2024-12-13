import matplotlib.pyplot as plt
from zacrostools.kmc_output import KMCOutput


kmc_output = KMCOutput(path='./results_kmc', analysis_range=[0, 100], range_type='time', weights='time')

plt.figure(figsize=(5, 4))
for surf_species in kmc_output.surf_species_names:
    av_coverage = kmc_output.av_coverage[surf_species]
    if av_coverage >= 1.0:
        plt.plot(kmc_output.time, kmc_output.coverage[surf_species],
                 label=f"{surf_species}")

plt.xlabel('Simulated time (s)')
plt.ylabel('Surface coverage (%)')
plt.legend()
plt.tight_layout()
plt.savefig('CoverageAllSites.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
