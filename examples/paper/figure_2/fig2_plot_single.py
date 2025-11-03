from zacrostools.kmc_output import KMCOutput
from zacrostools.procstat_output import plot_event_frequency
import matplotlib.pyplot as plt

kmc_output = KMCOutput(job_path='simulation_files',
                       analysis_range=[0, 100],
                       range_type='time',
                       weights='time')

fig, axs = plt.subplots(1, 2, figsize=(6, 2.7), sharex=True)

# Plot surface coverage
for surf_spec_name in kmc_output.surf_specs_names:
    if kmc_output.av_coverage[surf_spec_name] >= 1.0:
        axs[0].plot(kmc_output.time,
                    kmc_output.coverage[surf_spec_name],
                    label=surf_spec_name)

# Plot production of gas-phase species
for gas_spec_name in kmc_output.gas_specs_names:
    if kmc_output.tof[gas_spec_name] >= 0.0:
        axs[1].plot(kmc_output.time,
                    kmc_output.production[gas_spec_name],
                    label=gas_spec_name + '$_{(g)}$')

for ax in axs:
    ax.legend()
plt.tight_layout()

plt.savefig(f'/Users/hprats/Desktop/Figure_2A.pdf', bbox_inches='tight', transparent=False)

# Plot event frequencies
fig, axs = plt.subplots(1, figsize=(7, 3.5))
plot_event_frequency(ax=axs,
                     simulation_path='simulation_files',
                     analysis_range=[0, 100],
                     range_type='time')

plt.tight_layout()
plt.savefig(f'/Users/hprats/Desktop/Figure_2B.pdf', bbox_inches='tight', transparent=False)
plt.show()
