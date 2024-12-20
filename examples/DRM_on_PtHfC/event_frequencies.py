import matplotlib.pyplot as plt
from zacrostools.procstat_output import plot_procstat, parse_procstat_output_file

# Plot parameters
job_path = 'simulation_results/CH4_5.179e-04#CO2_6.105e-04'
analysis_range = [50, 100]
range_type = 'time'

df_procstat, delta_time, area = parse_procstat_output_file(
    output_file=f'{job_path}/procstat_output.txt',
    analysis_range=analysis_range,
    range_type=range_type
)

num_steps = len(df_procstat.index)
fig_height = max(4.0, num_steps * 0.18)

fig1, axs = plt.subplots(1, figsize=(9, fig_height))

plot_procstat(ax=axs,
              simulation_path=job_path,
              analysis_range=analysis_range,
              range_type=range_type)

plt.tight_layout(pad=3.0)  # Increased padding for better spacing
plt.savefig('event_frequencies.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
