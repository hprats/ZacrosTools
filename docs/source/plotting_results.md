# Plotting Results

This document provides instructions for generating plots from finished *Zacros* simulations using the 
`zacrostools` library. It includes examples for both single simulation results and contour plots from multiple 
simulations at various operating conditions.

## Plots from a Single KMC Simulation

### Surface Coverage vs. Simulated Time

he following example demonstrates how to plot surface coverage as a function of simulated time for a single KMC 
simulation.

```python
import matplotlib.pyplot as plt
from zacrostools.kmc_output import KMCOutput
kmc_output = KMCOutput(path='.', window_percent=[50, 100], window_type='time', weights='time')

plt.figure(figsize=(6, 4.5))

for site_type in kmc_output.site_types:
    for surf_species in kmc_output.coverage_per_site_type[site_type]:
        coverage = kmc_output.av_coverage_per_site_type[site_type][surf_species]
        if coverage >= 1.0:
            plt.plot(kmc_output.time, kmc_output.coverage_per_site_type[site_type][surf_species],
                     label=f"{surf_species} ({site_type})")

plt.xlabel('Simulated time (s)')
plt.ylabel('Surface coverage (%)')
plt.legend()
plt.tight_layout()
plt.show()
```

<div style="text-align: center;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/tests/plot_multiple_runs/Coverage.png?raw=true" alt="Coverage" width="400"/>
</div>

### Molecules Produced vs. Simulated Time

This example shows how to plot the number of molecules produced over simulated time in a single KMC simulation.

```python
import matplotlib.pyplot as plt
from zacrostools.kmc_output import KMCOutput

kmc_output = KMCOutput(path='.', window_percent=[50, 100], window_type='time', weights='time')

plt.figure(figsize=(8, 6))

for gas_species in kmc_output.gas_species_names:
    if kmc_output.tof[gas_species] > 0.0 and kmc_output.production[gas_species][-1] > 0:
        plt.plot(kmc_output.time, kmc_output.production[gas_species], linewidth=2, label=gas_species + '$_{(g)}$')

plt.xlabel('Time (s)')
plt.ylabel('Molecules produced')
plt.title('Molecules produced as a function of simulated time', fontsize=16)
plt.tight_layout()
plt.show()
```

<div style="text-align: center;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/tests/plot_multiple_runs/MoleculesProduced.png?raw=true" alt="MoleculesProduced" width="400"/>
</div>

## Contour Plots from a Set of KMC Simulations

When running a set of KMC simulations at various operating conditions, contour plots for (*p<sub>A</sub>,
p<sub>B</sub>*) or (*p<sub>A</sub>, T*) scans can be easily created using the 
{py:func}`zacrostools.plot_functions.plot_contour` function.

### Main Parameters (Mandatory for All Plots)

- **ax** (*matplotlib.axes.Axes*): Axis object where the contour plot should be created.
- **scan_path** (*str*): Path of the directory containing all the scan jobs.
- **x** (*str*): Magnitude to plot on the x-axis. Possible values:
  - `'pressure_X'`, where `X` is a gas species
  - `'temperature'`
- **y** (*str*): Magnitude to plot on the y-axis. Possible values:
  - `'pressure_Y'`, where `Y` is a gas species
  - `'temperature'`
- **z** (*str*): Magnitude to plot on the z-axis. Possible values:
  - `'tof'`, TOF (in log10)
  - `'tof_dif'`, difference in TOF between two systems (in log10) 
  - `'selectivity'`, selectivity (in %)
  - `'coverage'`, coverage (in %)
  - `'phase_diagram'`, most dominant surface species
  - `'final_time'`, final time (in log10)
  - `'final_energy'`, final energy
  - `'energy_slope'`, energy slope
  - `'has_issues'`, to check for issues

Depending on the type of plot (**z**), some additional parameters might be needed (see bellow).

### Optional Parameters

- **levels** (*list*): Defines the contour lines/regions. Default is `[-3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3]` for TOF plots, and `[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]` for selectivity plots.
- **cmap** (*str*): Colormap used to map scalar data to colors. Accepts colormap instances or registered names.
- **show_points** (*bool*): Displays grid points as black dots if `True`. Default is `False`.
- **show_colorbar** (*bool*): Displays the colorbar if `True`. Default is `True`.
- **auto_title** (*bool*): Automatically generates titles for subplots if `True`. Default is `False`.

### Contour Plot Types

#### TOF (Turnover Frequency)

##### Additional required parameters

- **min_molec** (*int*): Minimum number of product molecules required to calculate and plot TOF. Default is `0`.
- **window_percent** (*list*): Specifies the percentage range of the simulation time or events to consider, e.g., `[0, 100]`.
- **window_type** (*str*): The type of window to apply. Possible values:
  - `'time'` (based on simulated time)
  - `'nevents'` (based on the number of events)

##### Example

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_contour

fig, axs = plt.subplots(1, figsize=(5.5, 4.5))

plot_contour(ax=axs, scan_path="./scan_results_POM_1000K_PtHfC", x="pressure_CH4", y="pressure_O2", z="tof",
             gas_spec="H2", window_percent=[50, 100], window_type="time")

plt.tight_layout()
plt.savefig('ContourTof.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/tests/plot_multiple_runs/ScanTof.png?raw=true" alt="ScanTof" width="400"/>
</div>

#### TOF difference

##### Additional required parameters

- **scan_path_ref** (*str*): Path to the directory containing reference scan job results. Default is `None`.
- **min_molec** (*int*): Minimum number of product molecules required to calculate and plot TOF. Default is `0`.
- **window_percent** (*list*): Percentage range of the simulation time or events to consider, e.g., `[0, 100]`.
- **window_type** (*str*): Type of window to apply. Possible values:
  - `'time'` (based on simulated time)
  - `'nevents'` (based on the number of events)

##### Example

```python
# TODO 
```

#### Selectivity

##### Additional required parameters

- **main_product** (*str*): The main product for selectivity calculation.
- **side_products** (*list*): List of side products for selectivity calculation.
- **min_molec** (*int*): Minimum number of product molecules required to calculate and plot selectivity. Default is `0`.
- **window_percent** (*list*): Percentage range of the simulation time or events to consider, e.g., `[0, 100]`.
- **window_type** (*str*): Type of window to apply. Possible values:
  - `'time'` (based on simulated time)
  - `'nevents'` (based on the number of events)

##### Example

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_contour

fig, axs = plt.subplots(1, figsize=(5.5, 4.5))

plot_contour(ax=axs, scan_path="./scan_results_POM_1000K_PtHfC", x="pressure_CH4", y="pressure_O2",
             z="selectivity", main_product="H2", side_products=["H2O"], window_percent=[50, 100], window_type="time",
             min_molec=10)

plt.tight_layout()
plt.savefig('ScanSelectivity.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/tests/plot_multiple_runs/ScanSelectivity.png?raw=true" alt="ScanSelectivity" width="400"/>
</div>

#### Coverage

##### Additional required parameters

- **surf_spec** (*str*): Surface species for coverage plots.
- **site_type** (*str*): Name of site type. Default is `'default'`.
- **window_percent** (*list*): Percentage range of the simulation time or events to consider, e.g., `[0, 100]`.
- **window_type** (*str*): Type of window to apply. Possible values:
  - `'time'` (based on simulated time)
  - `'nevents'` (based on the number of events)
- **weights** (*str*): Weights for the averages. Possible values:
  - `'time'`
  - `'nevents'`
  - `None` (all weights are set to 1). Default is `None`.

##### Example (total coverage)

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_contour

fig, axs = plt.subplots(1, 2, figsize=(10, 4.5))

site_types = ['tC', 'tM']
for n, site_type in enumerate(site_types):
    plot_contour(ax=axs[n], scan_path="./scan_results_POM_1000K_PtHfC", x="pressure_CH4", y="pressure_O2", z="coverage",
                 surf_spec="total", site_type=site_type, window_percent=[50, 100], window_type="time")

plt.tight_layout()
plt.savefig('ScanCoverageTotal.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
```

![ScanCoverageTotal](https://github.com/hprats/ZacrosTools/blob/main/tests/plot_multiple_runs/ScanCoverageTotal.png?raw=true)

##### Example (coverage of a specific surface species)

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_contour

fig, axs = plt.subplots(1, 2, figsize=(10, 4.5))

site_types = ['tC', 'tM']
for n, site_type in enumerate(site_types):
    plot_contour(ax=axs[n], scan_path="./scan_results_POM_1000K_PtHfC", x="pressure_CH4", y="pressure_O2", z="coverage",
                 surf_spec="total", site_type=site_type, window_percent=[50, 100], window_type="time")

plt.tight_layout()
plt.savefig('ScanCoverageTotal.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
```

![ScanCoverageSpecific](https://github.com/hprats/ZacrosTools/blob/main/tests/plot_multiple_runs/ScanCoverageSpecific.png?raw=true)

#### Phase diagram

##### Additional required parameters

- **site_type** (*str*): Name of the site type. Default is `'default'`.
- **min_coverage** (*float*): Minimum total coverage required to plot the dominant surface species. Default is `20.0`.
- **surf_spec_values** (*list*): List of surface species to include in the phase diagram. If `None`, all species are included. Default is `None`.
- **tick_values** (*list*): Tick marks for the colorbar. If `None`, they are determined automatically. Default is `None`.
- **ticks_labels** (*list*): Labels for the colorbar ticks. If `None`, they are determined automatically. Default is `None`.
- **window_percent** (*list*): Percentage range of the simulation time or events to consider, e.g., `[0, 100]`.
- **window_type** (*str*): Type of window to apply. Possible values:
  - `'time'` (based on simulated time)
  - `'nevents'` (based on the number of events)
- **weights** (*str*): Weights for averaging. Possible values:
  - `'time'`
  - `'nevents'`
  - `None` (all weights set to 1). Default is `None`.

##### Example

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_contour

surf_spec_values = {
    'CH3': 0.5, 'CH2': 0.5, 'CH': 0.5, 'C': 0.5, 'CH3_Pt': 0.5, 'CH2_Pt': 0.5, 'CH_Pt': 0.5, 'C_Pt': 0.5,
    'CHO': 1.5, 'CO': 2.5, 'CO_Pt': 2.5, 'COOH': 3.5, 'COOH_Pt': 3.5, 'CO2': 4.5, 'CO2_Pt': 4.5, 'H': 5.5,
    'H2O': 6.5, 'H2O_Pt': 6.5, 'OH': 7.5, 'OH_Pt': 7.5, 'O': 8.5, 'O_Pt': 8.5, 'O2_Pt': 8.5}

tick_values = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5]
tick_labels = ['$CH_{x}$', '$CHO$', '$CO$', '$COOH$', '$CO_{2}$', '$H$', '$H_{2}O$', '$OH$', '$O$']

fig, axs = plt.subplots(1, 3, figsize=(10, 2.8))

site_types = ['tC', 'tM', 'Pt']
for n, site_type in enumerate(site_types):
    plot_contour(ax=axs[n], scan_path="./scan_results_POM_1000K_PtHfC", x="pressure_CH4", y="pressure_O2",
                 z="phase_diagram", site_type=site_type, window_percent=[50, 100], window_type="time",
                 surf_spec_values=surf_spec_values, tick_values=tick_values, tick_labels=tick_labels)

plt.tight_layout()
plt.savefig('ScanPhaseDiagram.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
```

![ScanPhaseDiagram](https://github.com/hprats/ZacrosTools/blob/main/tests/plot_multiple_runs/ScanPhaseDiagram.png?raw=true)

#### Final time

##### Additional required parameters

None.

##### Example

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_contour

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

plot_contour(ax=axs, scan_path="./scan_results_POM_1000K_PtHfC", x="pressure_CH4", y="pressure_O2", z="final_time")

plt.tight_layout()
plt.savefig('ScanFinalTime.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/tests/plot_multiple_runs/ScanFinalTime.png?raw=true" alt="ScanFinalTime" width="400"/>
</div>

#### Energy slope

##### Additional required parameters

- **window_percent** (*list*): Percentage range of the simulation time or events to consider, e.g., `[0, 100]`.
- **window_type** (*str*): Type of window to apply. Possible values:
  - `'time'` (based on simulated time)
  - `'nevents'` (based on the number of events)

```{tip}
For `z = 'energy_slope'` plots, set `window_percent = [50, 100]` and `window_type = 'nevents'`.
```

##### Example

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_contour

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

plot_contour(ax=axs, scan_path="./scan_results_POM_1000K_PtHfC", x="pressure_CH4", y="pressure_O2", z="energy_slope",
             window_percent=[50, 100], window_type='nevents')

plt.tight_layout()
plt.savefig('ScanEnergySlope.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/tests/plot_multiple_runs/ScanEnergySlope.png?raw=true" alt="ScanEnergySlope" width="400"/>
</div>

#### Issues

##### Additional required parameters

- **window_percent** (*list*): A list of two elements `[initial_percent, final_percent]` specifying the window of the 
total simulation. The values should be between 0 and 100, representing the percentage of the total simulated time or 
the total number of events to be considered. 
  - Default: `[0, 100]`

```{tip}
For `z = 'issues'` plots, set `window_percent = [50, 100]`. The `window_type` is automatically set to `'nevents'`.
```

##### Example

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_contour

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

plot_contour(ax=axs, scan_path="./scan_results_POM_1000K_PtHfC", x="pressure_CH4", y="pressure_O2", z="has_issues",
             window_percent=[50, 100])

plt.tight_layout()
plt.savefig('ScanIssues.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
```
<div style="text-align: center;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/tests/plot_multiple_runs/ScanIssues.png?raw=true" alt="ScanIssues" width="400"/>
</div>


### Example with multiple types of plots

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_contour

# Parameters for the figures
products = ['CO2', 'H2', 'CH4', 'O2']
site_types = ['tM', 'tC']
ignore = 30
min_molec = 5
x = "pressure_CO"
y = "pressure_H2O"
scan_path = '/scan_WGS_1000K'

fig, axs = plt.subplots(3, 4, figsize=(11, 6), sharey='row', sharex='col')

# TOF
for n, product in enumerate(products):
    plot_contour(ax=axs[0, n], scan_path=scan_path, x=x, y=y, z=f"tof_{product}", ignore=ignore, min_molec=min_molec)

# Total coverage
for n, site_type in enumerate(site_types):
    plot_contour(ax=axs[1, n], scan_path=scan_path, x=x, y=y, z="coverage_total", ignore=ignore, site_type=site_type,
                 weights='time')

# Phase diagrams
for n, site_type in enumerate(site_types):
    plot_contour(ax=axs[1, n + 2], scan_path=scan_path, x=x, y=y, z="phase_diagram", ignore=ignore, site_type=site_type,
                 weights='time')

# Selectivity
plot_contour(ax=axs[2, 0], scan_path=scan_path, x=x, y=y, z='selectivity', main_product='CO2',
             side_products=['CH4'], ignore=ignore, min_molec=min_molec)

# Final simulation time
plot_contour(ax=axs[2, 1], scan_path=scan_path, x=x, y=y, z='final_time')

# Final simulation energy
plot_contour(ax=axs[2, 2], scan_path=scan_path, x=x, y=y, z='final_energy')

plt.tight_layout()
plt.show()
plt.savefig("results_scan.pdf", bbox_inches='tight', transparent=False)
```
![ScanMultipleTypes](https://github.com/hprats/ZacrosTools/blob/main/tests/plot_multiple_runs/ScanMultipleTypes.png?raw=true)

```{warning}
This section of the documentation is under development.
```
