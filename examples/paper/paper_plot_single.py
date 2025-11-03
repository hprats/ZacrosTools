# Read simulation data here
# (…)

import matplotlib.pyplot as plt

# Plot surface coverage
plt.figure(figsize=(5, 4))
for surf_spec_name in kmc_output.surf_specs_names:
    av_cov = kmc_output.av_coverage[surf_spec_name]
    if av_cov >= 1.0:
        plt.plot(
            kmc_output.time,
            kmc_output.coverage[surf_spec_name],
            label=surf_spec_name)
plt.xlabel('Simulated time (s)')
plt.ylabel('Surface coverage (%)')
plt.legend()
plt.tight_layout()

# Plot production of gas-phase species
plt.figure(figsize=(5, 4))
for gas_spec_name in kmc_output.gas_specs_names:
    tof = kmc_output.tof[gas_spec_name]
    if tof >= 0.0:
        plt.plot(
            kmc_output.time,
            kmc_output.production[gas_spec_name],
            label=gas_spec_name + '$_{(g)}$')
plt.xlabel('Simulated time (s)')
plt.ylabel('Molecules produced')
plt.legend()
plt.tight_layout()

plt.show()
