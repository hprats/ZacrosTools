import matplotlib.pyplot as plt
from zacrostools.kmc_output import KMCOutput


kmc_output = KMCOutput(path='./results_kmc', window_percent=[0, 100], window_type='time', weights='time')

plt.figure(figsize=(6, 4.5))
for gas_species in kmc_output.gas_species_names:
    if kmc_output.tof[gas_species] > 0.0 and kmc_output.production[gas_species][-1] > 0:
        plt.plot(kmc_output.time, kmc_output.production[gas_species], linewidth=2, label=gas_species + '$_{(g)}$')

plt.xlabel('Simulated time (s)')
plt.ylabel('Molecules produced')
plt.legend()
plt.tight_layout()
plt.savefig('MoleculesProduced.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
