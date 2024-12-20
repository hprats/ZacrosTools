import matplotlib.pyplot as plt
from zacrostools.procstat_output import plot_procstat, parse_procstat_output_file

# Plot parameters
job_path = 'simulation_results/CH4_5.179e-04#CO2_6.105e-04'
analysis_range = [50, 100]
range_type = 'time'
hide_diffusion_steps = False

df_procstat, delta_time, area = parse_procstat_output_file(
    output_file=f'{job_path}/procstat_output.txt',
    analysis_range=analysis_range,
    range_type=range_type
)

if hide_diffusion_steps:
    elementary_steps = df_procstat[
        (df_procstat['noccur_net'] != 0) & (~df_procstat.index.str.startswith('d'))
        ].index.tolist()
else:
    elementary_steps = df_procstat[
        (df_procstat['noccur_net'] != 0)
    ].index.tolist()

grouping = {
    'aCH4_Pt': ['aCH4_Pt-1', 'aCH4_Pt-2'],
    'aCH4_in': ['aCH4_in-1', 'aCH4_in-2'],
    'aO2_Pt': ['aO2_Pt-1', 'aO2_Pt-2'],
    'aH2_in': ['aH2_in_CH-1', 'aH2_in_CH-2', 'aH2_in_CH-3', 'aH2_in_CH-4',
               'aH2_in_C-1', 'aH2_in_C-2', 'aH2_in_C-3', 'aH2_in_C-4'],
    'bCH3_Pt': ['bCH3_Pt-1', 'bCH3_Pt-2'],
    'bCH3_in': ['bCH3_in-1', 'bCH3_in-2'],
    'bCH2_in': ['bCH2_in-1', 'bCH2_in-2'],
    'bCH_in': ['bCH_in-1', 'bCH_in-2', 'bCH_in-3', 'bCH_in-4'],
    'fCO_in': ['fCO_in-1', 'fCO_in-2', 'fCO_in-3', 'fCO_in-4'],
    'CHtoCHO_in': ['CHtoCHO_in-1', 'CHtoCHO_in-2', 'CHtoCHO_in-3', 'CHtoCHO_in-4'],
    'CHOtoCO_Pt': ['CHOtoCO_Pt-1', 'CHOtoCO_Pt-2'],
    'CHOtoCO_in': ['CHOtoCO_in-1', 'CHOtoCO_in-2'],
    'CtoCOH_in': ['CtoCOH_in-1', 'CtoCOH_in-2'],
    'fOH_Pt': ['fOH_Pt-1', 'fOH_Pt-2'],
    'fOH_in': ['fOH_in_a-1', 'fOH_in_a-2', 'fOH_in_b-1'],
    'fH2O_Pt': ['fH2O_Pt-1', 'fH2O_Pt-2'],
    'fH2O_in': ['fH2O_in-1', 'fH2O_in-2'],
    'CO2toCOOH_in': ['CO2toCOOH_in-1', 'CO2toCOOH_in-2'],
    'COOHtoCO_Pt': ['COOHtoCO_Pt-1', 'COOHtoCO_Pt-2'],
    'COOHtoCO_in': ['COOHtoCO_in-1', 'COOHtoCO_in-2'],
    'dO_in': ['dO_in-1', 'dO_in-2'],
    'dCH3_in': ['dCH3_in-1', 'dCH3_in-2'],
    'dCH2_in': ['dCH2_in-1', 'dCH2_in-2'],
    'dCH_in': ['dCH_in-1', 'dCH_in-2', 'dCH_in-3', 'dCH_in-4'],
    'dCHO_in': ['dCHO_in-1', 'dCHO_in-2'],
    'dCOH_in': ['dCOH_in-1', 'dCOH_in-2'],
}

num_unique_groups = len(grouping)
grouped_steps = set()
for steps in grouping.values():
    grouped_steps.update(steps)
steps_not_grouped = set(elementary_steps) - grouped_steps
num_steps_not_grouped = len(steps_not_grouped)
total_steps = num_unique_groups + num_steps_not_grouped
fig_height = max(4.0, total_steps * 0.18)

fig1, axs = plt.subplots(
    1,
    figsize=(9, fig_height),
    sharey='row',
    sharex='col'
)

plot_procstat(
    ax=axs,
    simulation_path=job_path,
    analysis_range=analysis_range,
    range_type=range_type,
    elementary_steps=None,
    hide_zero_events=True,
    grouping=grouping
)

plt.tight_layout(pad=3.0)  # Increased padding for better spacing
plt.savefig('event_frequencies_grouping.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
