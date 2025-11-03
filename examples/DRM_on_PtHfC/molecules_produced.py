import matplotlib.pyplot as plt
from zacrostools.kmc_output import KMCOutput

kmc_output = KMCOutput(
    path='simulation_results/CH4_3.728e-01#CO2_4.394e-01',
    analysis_range=[0, 100],
    range_type='time',
    weights='time')

plt.figure(figsize=(5, 4))
for gas_spec_name in kmc_output.gas_specs_names:
    if kmc_output.tof[gas_spec_name] > 0.0 and kmc_output.production[gas_spec_name][-1] > 0:
        plt.plot(kmc_output.time, kmc_output.production[gas_spec_name], linewidth=2, label=gas_spec_name + '$_{(g)}$')

plt.xlabel('Simulated time (s)')
plt.ylabel('Molecules produced')
plt.legend()

plt.tight_layout()
plt.savefig('molecules_produced.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
