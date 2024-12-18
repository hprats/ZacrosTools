import matplotlib.pyplot as plt
from zacrostools.kmc_output import KMCOutput

kmc_output = KMCOutput(
    path='simulation_results/CH4_3.728e-01#CO2_4.394e-01',
    analysis_range=[0, 100],
    range_type='time',
    weights='time')

plt.figure(figsize=(5, 4))
for surf_spec_name in kmc_output.surf_specs_names:
    av_coverage = kmc_output.av_coverage[surf_spec_name]
    if av_coverage >= 1.0:
        plt.plot(kmc_output.time, kmc_output.coverage[surf_spec_name],
                 label=surf_spec_name)

plt.xlabel('Simulated time (s)')
plt.ylabel('Surface coverage (%)')
plt.legend()

plt.tight_layout()
plt.savefig('coverage_per_totalsites.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()

