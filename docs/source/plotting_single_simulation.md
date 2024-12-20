# Plotting single simulation results

There are several ways to visualize results from a single KMC simulation. This section demonstrates how to plot surface coverage and the number of molecules produced over time.

### Surface coverage

In this example, we plot surface coverage as a function of simulation time for different surface species. The `KMCOutput` object is initialized with data from a completed KMC simulation, and the plot displays the coverage for all species that reach a threshold coverage of 1%.

```python
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
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/coverage_per_totalsites.png?raw=true" alt="Coverage per total sites" width="500"/> </div>


In the previous example, coverage is calculated by dividing the number of molecules of a given adsorbate by the total number of sites. However, it is often more meaningful to calculate coverage as the number of molecules of a specific adsorbate on a particular site type, divided by the total number of sites of that type. The following example demonstrates how to do this:

```python
import matplotlib.pyplot as plt
from zacrostools.kmc_output import KMCOutput

kmc_output = KMCOutput(
    path='simulation_results/CH4_3.728e-01#CO2_4.394e-01',
    analysis_range=[0, 100],
    range_type='time',
    weights='time')

fig, axs = plt.subplots(1, len(kmc_output.site_types),
                        figsize=(2.7 * len(kmc_output.site_types), 3), sharey='all')

for i, site_type in enumerate(kmc_output.site_types):
    for surf_spec_name in kmc_output.coverage_per_site_type[site_type]:
        av_coverage = kmc_output.av_coverage_per_site_type[site_type][surf_spec_name]
        if av_coverage >= 1.0:
            axs[i].plot(kmc_output.time, kmc_output.coverage_per_site_type[site_type][surf_spec_name],
                        label=surf_spec_name)
    axs[i].set_title(site_type)
    axs[i].legend()

axs[0].set_xlabel('Simulated time (s)')
axs[1].set_xlabel('Simulated time (s)')
axs[0].set_ylabel('Surface coverage (%)')

plt.tight_layout()
plt.savefig('coverage_per_sitetype.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/coverage_per_sitetype.png?raw=true" alt="Coverage per site type" width="700"/> </div>

---

### Number of molecules produced

This example demonstrates how to plot the number of molecules produced over time for different gas-phase species in a single KMC simulation.

```python
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
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/molecules_produced.png?raw=true" alt="Molecules produced" width="500"/> </div>

---

### Event frequencies

The frequency of different types of events can provide valuable insights into the reaction mechanism. The `procstat_output.txt` file contains statistical information about the events (elementary steps) that occurred during the simulation. By parsing this file, one can plot the frequency of each event over a specified time range. 

#### Simple plot of event frequencies

The following example demonstrates how to plot the frequency of all observed events in a specified time range without applying any grouping of similar events:

```python
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
```

This code reads the `procstat_output.txt` file, filters the data for the specified time range, and then plots each elementary step event frequency. The vertical size of the figure is dynamically adjusted based on the number of elementary steps.

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/event_frequencies.png?raw=true" alt="Stiffness coefficients" width="700"/> </div>

---

#### Grouped event frequencies and selective hiding of events

Sometimes, there may be too many elementary steps to analyze individually. Grouping related events together simplifies the visualization. Additionally, one may want to hide certain types of events, such as diffusion steps, to focus on reaction events only. The following example demonstrates how to group similar events and optionally hide diffusion steps:

```python
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

# Define groups of related elementary steps
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
```

In this example, events are grouped for clearer visualization. Additionally, by setting `hide_diffusion_steps` to `True`, diffusion steps can be filtered out, making it easier to focus on specific reaction events. The dynamic figure sizing and grouping enable a much more manageable and interpretable plot, especially for complex reaction networks.

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/event_frequencies_grouping.png?raw=true" alt="Stiffness coefficients" width="700"/> </div>

### Stiffness scaling coefficients

In simulations where stiffness scaling is employed, it's often useful to visualize how the stiffness coefficients evolve over time. Stiffness coefficients may remain constant for a while and then abruptly change at specific times. Using a step plot makes it easy to highlight these jumps:

```python
import numpy as np
import matplotlib.pyplot as plt
from zacrostools.kmc_output import parse_general_output_file

data = parse_general_output_file(
    output_file="simulation_results/CH4_5.179e-04#CO2_6.105e-04/general_output.txt",
    parse_stiffness_coefficients=True)

stiffness_df = data['stiffness_scaling_coefficients']

# Identify columns corresponding to stiffness steps
step_columns = [col for col in stiffness_df.columns if col not in ['time', 'nevents']]

# Filter out steps where all coefficients are 1.0 (no change)
filtered_steps = [col for col in step_columns if not np.all(np.isclose(stiffness_df[col], 1.0))]

plt.figure(figsize=(8, 6))
for step in filtered_steps:
    plt.step(
        stiffness_df['time'],
        stiffness_df[step],
        where='post',
        label=step,
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
```

The `parse_general_output_file` function extracts stiffness scaling coefficients from the general output file of a simulation. After filtering out steps that do not change (remain at a factor of 1.0), the code creates a step plot showing how the coefficients evolve over time. 

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/stiffness_coefficients.png?raw=true" alt="Stiffness coefficients" width="600"/> </div>

---