import numpy as np
import matplotlib.pyplot as plt
from zacrostools.kmc_output import parse_general_output_file

data = parse_general_output_file(
    output_file="simulation_results/CH4_3.728e-01#CO2_4.394e-01/general_output.txt",
    parse_stiffness_coefficients=True)

stiffness_df = data['stiffness_scaling_coefficients']

# Exclude from the plot steps where all stiffness coefficients are 1.0
step_columns = [col for col in stiffness_df.columns if col not in ['time', 'nevents']]
filtered_steps = [col for col in step_columns if not np.all(np.isclose(stiffness_df[col], 1.0))]

plt.figure(figsize=(8, 6))
for step in filtered_steps:
    plt.plot(
        stiffness_df['time'],
        stiffness_df[step],
        label=step,
        marker='o',
        linestyle='-',
        linewidth=1.5
    )

plt.yscale('log')
plt.xlabel('Simulated time (s)', fontsize=14)
plt.ylabel('Stiffness coefficient', fontsize=14)
plt.legend(fontsize=12, title_fontsize=12)
plt.grid(True, which="both", ls="--", linewidth=0.5)

plt.tight_layout()
plt.savefig('stiffness_coefficients.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
