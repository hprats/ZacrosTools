# Plotting Results

This document provides instructions for generating plots from finished *Zacros* simulations using the 
`zacrostools` library. This section includes examples for visualizing results from a single simulation and generating 
heatmap plots from multiple simulations at different operating conditions.

---

## 1. Plotting Results from a Single KMC Simulation

To plot the main results for a single KMC run, create a `KMCOutput` object and extract the relevant data for plotting. 
Below are examples demonstrating how to plot surface coverage and the number of molecules produced over time.

### Coverage

In this example, we plot surface coverage as a function of simulation time for different surface species. The `KMCOutput` 
object is initialized with data from a finished KMC simulation, and the plot displays the coverage for all species that reach a threshold coverage of 1%.

```python
import matplotlib.pyplot as plt
from zacrostools.kmc_output import KMCOutput

kmc_output = KMCOutput(path='./results_kmc', window_percent=[0, 100], window_type='time', weights='time')

plt.figure(figsize=(5, 4))
for surf_species in kmc_output.surf_species_names:
    av_coverage = kmc_output.av_coverage[surf_species]
    if av_coverage >= 1.0:
        plt.plot(kmc_output.time, kmc_output.coverage[surf_species],
                 label=f"{surf_species}")

plt.xlabel('Simulated time (s)')
plt.ylabel('Surface coverage (%)')
plt.legend()
plt.tight_layout()
plt.savefig('CoverageAllSites.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/docs/images/plot_single_run/CoverageAllSites.png?raw=true" alt="CoverageAllSites" width="500"/>
</div>

In the previous example, coverage is calculated by dividing the number of molecules of a given adsorbate by the total 
number of sites. However, it is often more meaningful to calculate coverage as the number of molecules of a specific 
adsorbate on a particular site type, divided by the total number of sites of that type. The following example 
demonstrates how to do this:

```python
import matplotlib.pyplot as plt
from zacrostools.kmc_output import KMCOutput

kmc_output = KMCOutput(path='./results_kmc', window_percent=[0, 100], window_type='time', weights='time')

fig, axs = plt.subplots(1, len(kmc_output.site_types), figsize=(3 * len(kmc_output.site_types), 4), sharey='all')

for i, site_type in enumerate(kmc_output.site_types):
    for surf_species in kmc_output.coverage_per_site_type[site_type]:
        av_coverage = kmc_output.av_coverage_per_site_type[site_type][surf_species]
        if av_coverage >= 0.1:
            axs[i].plot(kmc_output.time, kmc_output.coverage_per_site_type[site_type][surf_species], label=surf_species)
    axs[i].set_title(site_type)
    axs[i].legend()

for i in range(len(kmc_output.site_types)):
    axs[i].set_xlabel('Simulated time (s)')
axs[0].set_ylabel('Surface coverage (%)')
plt.tight_layout()
plt.savefig('CoveragePerType.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/docs/images/plot_single_run/CoveragePerType.png?raw=true" alt="CoveragePerType" width="600"/>
</div>

### TOF

This example demonstrates how to plot the number of molecules produced over time for different gas-phase species in a single KMC simulation. 

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
plt.savefig('MoleculesProduced.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/docs/images/plot_single_run/MoleculesProduced.png?raw=true" alt="MoleculesProduced" width="500"/>
</div>

---

## 2. Heatmaps in 2D from a Set of KMC Simulations

When running a set of KMC simulations at various operating conditions, 2D heatmaps for (*p<sub>A</sub>,
p<sub>B</sub>*) or (*p<sub>A</sub>, T*) scans can be easily created using the 
{py:func}`zacrostools.plot_functions.plot_heatmap` function.

### Parameters

#### Mandatory for all plot types

- **ax** (*matplotlib.axes.Axes*): Axis object where the contour plot should be created.
- **scan_path** (*str*): Path of the directory containing all the scan jobs.
- **x** (*str*): Magnitude to plot on the x-axis. Possible values:
  - `'pressure_X'`, where `X` is a gas species
  - `'temperature'`
- **y** (*str*): Magnitude to plot on the y-axis. Possible values:
  - `'pressure_Y'`, where `Y` is a gas species
  - `'temperature'`
- **z** (*str*): Magnitude to plot on the z-axis. Possible values:
  - `'tof'`: log<sub>10</sub>TOF (molec·s<sup>-1</sup>·Å<sup>-2</sup>).
  - `'tof_dif'`: Difference in log<sub>10</sub>TOF between two systems.
  - `'selectivity'`: Selectivity (%).
  - `'coverage'`: Coverage (%).
  - `'phase_diagram'`: Most dominant surface species.
  - `'final_time'`: log<sub>10</sub>Final time (s).
  - `'final_energy'`: Final energy (eV·Å<sup>-2</sup>).
  - `'energy_slope'`: Energy slope (eV·Å<sup>-2</sup>·step<sup>-1</sup>).
  - `'has_issues'`: To check for issues.

Depending on the type of plot (`z`), some additional parameters might be needed (see bellow).

#### Optional

- **cmap** (*str*): Colormap used to map scalar data to colors. Accepts colormap instances or registered names.
- **show_points** (*bool*): Displays grid points as black dots if `True`. Default is `False`.
- **show_colorbar** (*bool*): Displays the colorbar if `True`. Default is `True`.
- **auto_title** (*bool*): Automatically generates titles for subplots if `True`. Default is `False`.

### Heatmap Types

#### TOF (Turnover Frequency)

`z = 'tof'`, plot the TOF (in molec·s<sup>-1</sup>·Å<sup>-2</sup>) of a given gas-phase species.

<div style="margin-left: 20px;">

**Additional parameters:**

Mandatory:

- **gas_spec** (*str*): Name of gas-phase species for the TOF calculation.

Optional:

- **min_molec** (*int*): Minimum product molecules for TOF calculation. Default is `0`. 
- **levels** (*list*): Specifies the contour levels for the plot. If `None`, the levels are automatically determined, with any TOF below `1.0e-06` set to this threshold. 
If provided, TOF values below the lowest value in levels are set to `min(levels)`. Default is `None`.
- **window_percent** (*list*): Specifies the percentage range of the simulation time or events to consider. Default is `[0, 100]`.
- **window_type** (*str*): The type of window to apply. Default is `time`. Possible values:
  - `'time'` (based on simulated time)
  - `'nevents'` (based on the number of events)

**Example:**

```python
import numpy as np
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

plot_heatmap(ax=axs, scan_path="./scan_results_POM_1000K_PtHfC", x="pressure_CH4", y="pressure_O2", z="tof",
             gas_spec="H2", window_percent=[50, 100], window_type="time", auto_title=True,
             levels=np.logspace(-3, 4, num=15), min_molec=0)

plt.tight_layout()
plt.savefig('ScanTof.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/docs/images/plot_multiple_runs/ScanTof.png?raw=true" alt="ScanTof" width="400"/>
</div>

#### TOF difference

`z = 'tof_dif'`, plot the TOF difference (∆TOF, in molec·s<sup>-1</sup>·Å<sup>-2</sup>) of a given gas-phase species between two simulations.

<div style="margin-left: 20px;">

**Additional parameters:**

Mandatory:

- **gas_spec** (*str*): Name of gas-phase species for the TOF calculation.
- **scan_path_ref** (*str*): Path to the directory containing reference scan job results.

Optional:

- **levels** (*list*): Defines the levels used in the colorbar. If `None`, the levels are automatically determined based on the data, with TOF differences below `1.0e-06` set to this value. 
If `levels` is provided, any TOF difference below the smallest value in levels is set to `min(levels)`. Default is `'None'`.
- **window_percent** (*list*): Percentage range of the simulation time or events to consider. Default is `[0, 100]`.
- **window_type** (*str*): Type of window to apply. Default is `time`. Possible values:
  - `'time'` (based on simulated time)
  - `'nevents'` (based on the number of events)

Note that `min_molec` parameter is not allowed in `z = 'tof_dif'` plots. 

**Example:**

```python
import numpy as np
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, figsize=(5, 3.5))

plot_heatmap(ax=axs, scan_path="./scan_results_POM_1000K_PtHfC", scan_path_ref="./scan_results_POM_1000K_HfC",
             x="pressure_CH4", y="pressure_O2", z="tof_dif",
             gas_spec="H2", window_percent=[50, 100], window_type="time", auto_title=True,
             levels=np.logspace(-3, 4, num=15))

plt.tight_layout()
plt.savefig('ScanTofDif.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/docs/images/plot_multiple_runs/ScanTofDif.png?raw=true" alt="ScanTofDif" width="500"/>
</div>

#### Selectivity

`z = 'selectivity'`, plot the selectivity (in %) towards a given gas-phase species.

<div style="margin-left: 20px;">

**Additional parameters:**

Mandatory:

- **main_product** (*str*): The main product for selectivity calculation.
- **side_products** (*list*): List of side products for selectivity calculation.

Optional:

- **min_molec** (*int*): Minimum value of main + side product molecules for selectivity calculation. 
If `None`, selectivity only calculated if main + side product molecules is greater than zero. Default is `None`; 
- **levels** (*list*): Defines the levels used in the colorbar. Default is `np.linspace(0, 100, 11, dtype=int)`. 
- **window_percent** (*list*): Percentage range of the simulation time or events to consider. Default is `[0, 100]`.
- **window_type** (*str*): Type of window to apply. Default is `time`. Possible values:
  - `'time'` (based on simulated time)
  - `'nevents'` (based on the number of events)

**Example**

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, figsize=(5.5, 4.5))

plot_heatmap(ax=axs, scan_path="./scan_results_POM_1000K_PtHfC", x="pressure_CH4", y="pressure_O2",
             z="selectivity", main_product="H2", side_products=["H2O"], window_percent=[50, 100], window_type="time",
             min_molec=10, auto_title=True)

plt.tight_layout()
plt.savefig('ScanSelectivity.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/docs/images/plot_multiple_runs/ScanSelectivity.png?raw=true" alt="ScanSelectivity" width="400"/>
</div>

#### Coverage

`z = 'coverage'`, plot the coverage (in %) of one or all surface species.

<div style="margin-left: 20px;">

**Additional parameters:**

Mandatory:

- **surf_spec** (*str*): Surface species for coverage plots.

Optional:

- **site_type** (*str*): Name of site type. Default is `'default'` (i.e., only valid if a default lattice model is used).
- **levels** (*list*): Defines the levels used in the colorbar. Default is `np.linspace(0, 100, 11, dtype=int)`. 
- **window_percent** (*list*): Percentage range of the simulation time or events to consider. Default is `[0, 100]`.
- **window_type** (*str*): Type of window to apply. Default is `time`. Possible values:
  - `'time'` (based on simulated time)
  - `'nevents'` (based on the number of events)
- **weights** (*str*): Weights for the averages. Default is `None`. Possible values:
  - `'time'`
  - `'nevents'`
  - `None` (all weights are set to 1).

**Example (total coverage)**

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, 2, figsize=(10, 4.5))

site_types = ['tC', 'tM']
for n, site_type in enumerate(site_types):
    plot_heatmap(ax=axs[n], scan_path="./scan_results_POM_1000K_PtHfC", x="pressure_CH4", y="pressure_O2", z="coverage",
                 surf_spec="total", site_type=site_type, window_percent=[50, 100], window_type="time", auto_title=True)

plt.tight_layout()
plt.savefig('ScanCoverageTotal.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
```

![ScanCoverageTotal](https://github.com/hprats/ZacrosTools/blob/main/docs/images/plot_multiple_runs/ScanCoverageTotal.png?raw=true)

**Example (coverage of a specific surface species)**

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, 2, figsize=(10, 4.5))

site_types = ['tC', 'tM']
for n, site_type in enumerate(site_types):
    plot_heatmap(ax=axs[n], scan_path="./scan_results_POM_1000K_PtHfC", x="pressure_CH4", y="pressure_O2", z="coverage",
                 surf_spec="total", site_type=site_type, window_percent=[50, 100], window_type="time", auto_title=True)

plt.tight_layout()
plt.savefig('ScanCoverageTotal.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
```

![ScanCoverageSpecific](https://github.com/hprats/ZacrosTools/blob/main/docs/images/plot_multiple_runs/ScanCoverageSpecific.png?raw=true)

#### Phase diagram

`z = 'phase_diagram'`, plot the most dominant surface species. 

<div style="margin-left: 20px;">

**Additional parameters:**

Optional:

- **site_type** (*str*): Name of the site type. Default is `'default'`.
- **min_coverage** (*float*): Minimum total coverage required to plot the dominant surface species. Default is `20.0`.
- **surf_spec_values** (*list*): List of surface species to include in the phase diagram. If `None`, all species are 
included. Default is `None`.
- **tick_values** (*list*): Tick marks for the colorbar. If `None`, they are determined automatically. Default is `None`.
- **ticks_labels** (*list*): Labels for the colorbar ticks. If `None`, they are determined automatically. Default is `None`.
- **window_percent** (*list*): Percentage range of the simulation time or events to consider. Default is `[0, 100]`.
- **window_type** (*str*): Type of window to apply. Default is `time`. Possible values:
  - `'time'` (based on simulated time)
  - `'nevents'` (based on the number of events)
- **weights** (*str*): Weights for averaging. Default is `None`. Possible values:
  - `'time'`
  - `'nevents'`
  - `None` (all weights set to 1).

**Example**

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

surf_spec_values = {
    'CH3': 0.5, 'CH2': 0.5, 'CH': 0.5, 'C': 0.5, 'CH3_Pt': 0.5, 'CH2_Pt': 0.5, 'CH_Pt': 0.5, 'C_Pt': 0.5,
    'CHO': 1.5, 'CO': 2.5, 'CO_Pt': 2.5, 'COOH': 3.5, 'COOH_Pt': 3.5, 'CO2': 4.5, 'CO2_Pt': 4.5, 'H': 5.5,
    'H2O': 6.5, 'H2O_Pt': 6.5, 'OH': 7.5, 'OH_Pt': 7.5, 'O': 8.5, 'O_Pt': 8.5, 'O2_Pt': 8.5}

tick_values = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5]
tick_labels = ['$CH_{x}$', '$CHO$', '$CO$', '$COOH$', '$CO_{2}$', '$H$', '$H_{2}O$', '$OH$', '$O$']

fig, axs = plt.subplots(1, 3, figsize=(10, 2.8))

site_types = ['tC', 'tM', 'Pt']
for n, site_type in enumerate(site_types):
    plot_heatmap(ax=axs[n], scan_path="./scan_results_POM_1000K_PtHfC", x="pressure_CH4", y="pressure_O2",
                 z="phase_diagram", site_type=site_type, window_percent=[50, 100], window_type="time",
                 surf_spec_values=surf_spec_values, tick_values=tick_values, tick_labels=tick_labels, 
                 auto_title=True)

plt.tight_layout()
plt.savefig('ScanPhaseDiagram.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
```

![ScanPhaseDiagram](https://github.com/hprats/ZacrosTools/blob/main/docs/images/plot_multiple_runs/ScanPhaseDiagram.png?raw=true)

#### Final time

`z = 'final_time'`, plot the final time of the simulation (in s).

<div style="margin-left: 20px;">

**Additional parameters:**

Optional:

- **levels** (*list*): Defines the levels used in the colorbar. If `None`, levels are automatically determined from the plot. Default is `None`. 

**Example**

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

plot_heatmap(ax=axs, scan_path="./scan_results_POM_1000K_PtHfC", x="pressure_CH4", y="pressure_O2", z="final_time", 
             auto_title=True)

plt.tight_layout()
plt.savefig('ScanFinalTime.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/docs/images/plot_multiple_runs/ScanFinalTime.png?raw=true" alt="ScanFinalTime" width="400"/>
</div>

#### Energy slope

`z = 'energy_slope'`, plot the slope of the lattice energy (in eV·Å<sup>-2</sup>·step<sup>-1</sup>).

A high slope of the lattice energy indicates that the simulation might have not reached the steady-state. 

<div style="margin-left: 20px;">

**Additional parameters:**

Optional:

- **levels** (*list*): Defines the levels used in the colorbar. Default is `np.logspace(-11, -8, num=7)`. 
- **window_percent** (*list*): Percentage range of the simulation time or events to consider. Default is `[0, 100]`.
- **window_type** (*str*): Type of window to apply. Default is `time`. Possible values:
  - `'time'` (based on simulated time)
  - `'nevents'` (based on the number of events)

```{tip}
For `z = 'energy_slope'` plots, set `window_percent = [50, 100]` and `window_type = 'nevents'`.
```

**Example**

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

plot_heatmap(ax=axs, scan_path="./scan_results_POM_1000K_PtHfC", x="pressure_CH4", y="pressure_O2", z="energy_slope",
             window_percent=[50, 100], window_type='nevents', auto_title=True)

plt.tight_layout()
plt.savefig('ScanEnergySlope.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/docs/images/plot_multiple_runs/ScanEnergySlope.png?raw=true" alt="ScanEnergySlope" width="400"/>
</div>

#### Simulation issues

To identify and visualize potential issues in simulations, set `z = 'issues'`. This plot displays a colored mesh that highlights simulations with detected problems.

<div style="margin-left: 20px;">

**Issue Detection Criteria:**
1. **Trend Analysis**: Positive or negative trends in lattice energy within the selected events window.
2. **Non-Linearity**: Deviations from linearity in the time vs. number of events plot within the selected events window.

These issues often arise from simulations that are too short (i.e., the system has not reached steady-state) or problems with the dynamic scaling algorithm. 
Be aware that false positives or negatives can occur, so manual verification of results is recommended.

**Additional required parameters:**

- **window_percent** (*list*): A list of two elements `[initial_percent, final_percent]` specifying the window of the 
total simulation. The values should be between 0 and 100, representing the percentage of the total simulated time or 
the total number of events to be considered. Default: `[30, 100]`

```{tip}
For `z = 'issues'` plots, `window_percent = [50, 100]` is recommended. The `window_type` is automatically set to `'nevents'`.
```

**Example**

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

plot_heatmap(ax=axs, scan_path="./scan_results_POM_1000K_PtHfC", x="pressure_CH4", y="pressure_O2", z="has_issues",
             window_percent=[50, 100], auto_title=True)

plt.tight_layout()
plt.savefig('ScanIssues.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/docs/images/plot_multiple_runs/ScanIssues.png?raw=true" alt="ScanIssues" width="400"/>
</div>

#### Multiple types of plots

Different types of heatmaps might be combined in a single figure, as shown in the following example:

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

scan_path = "./scan_results_POM_1000K_PtHfC"
x = "pressure_CH4"
y = "pressure_O2"
window_percent = [50, 100]
window_type = "time"
min_molec = 10

surf_spec_values = {
    'CH3': 0.5, 'CH2': 0.5, 'CH': 0.5, 'C': 0.5, 'CH3_Pt': 0.5, 'CH2_Pt': 0.5, 'CH_Pt': 0.5, 'C_Pt': 0.5,
    'CHO': 1.5, 'CO': 2.5, 'CO_Pt': 2.5, 'COOH': 3.5, 'COOH_Pt': 3.5, 'CO2': 4.5, 'CO2_Pt': 4.5, 'H': 5.5,
    'H2O': 6.5, 'H2O_Pt': 6.5, 'OH': 7.5, 'OH_Pt': 7.5, 'O': 8.5, 'O_Pt': 8.5, 'O2_Pt': 8.5}
tick_values = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5]
tick_labels = ['$CH_{x}$', '$CHO$', '$CO$', '$COOH$', '$CO_{2}$', '$H$', '$H_{2}O$', '$OH$', '$O$']


fig, axs = plt.subplots(4, 4, figsize=(11, 9), sharey='row', sharex='col')

for n, product in enumerate(['CO', 'H2', 'H2O', 'CO2']):
    plot_heatmap(ax=axs[0, n], scan_path=scan_path, x=x, y=y, z="tof", gas_spec=product,
                 window_percent=window_percent, window_type=window_type, auto_title=True)

for n, site_type in enumerate(['tC', 'tM', 'Pt']):
    plot_heatmap(ax=axs[1, n], scan_path=scan_path, x=x, y=y, z="coverage", surf_spec="total",
                 window_percent=window_percent, window_type=window_type,
                 site_type=site_type, weights="time", auto_title=True)

for n, site_type in enumerate(['tC', 'tM', 'Pt']):
    plot_heatmap(ax=axs[2, n], scan_path=scan_path, x=x, y=y, z="phase_diagram",
                 window_percent=window_percent, window_type=window_type, site_type=site_type,
                 surf_spec_values=surf_spec_values, tick_values=tick_values, tick_labels=tick_labels,
                 min_coverage=20, weights="time", auto_title=True)

plot_heatmap(ax=axs[3, 0], scan_path=scan_path, x=x, y=y, z='selectivity', main_product="H2",
             side_products=["H2O"], window_percent=window_percent, window_type=window_type, min_molec=min_molec,
             auto_title=True)

plot_heatmap(ax=axs[3, 1], scan_path=scan_path, x=x, y=y, z='final_time', auto_title=True)

plot_heatmap(ax=axs[3, 2], scan_path=scan_path, x=x, y=y, z='energy_slope', window_percent=window_percent,
             window_type='nevents', auto_title=True)

plot_heatmap(ax=axs[3, 3], scan_path=scan_path, x=x, y=y, z='issues', window_percent=window_percent,
             auto_title=True)

# Hide empty axes:
axs[1, 3].axis('off')
axs[2, 3].axis('off')

plt.tight_layout()
plt.savefig('ScanMultipleTypes.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
```
![ScanMultipleTypes](https://github.com/hprats/ZacrosTools/blob/main/docs/images/plot_multiple_runs/ScanMultipleTypes.png?raw=true)

### Customising the Plots

The size of axis ticks and fontsize of axis labels and titles can be adjusted with Matplotlib. Below are two examples 
that show how to do that.

For a plot with a single heatmap:

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

plot_heatmap(ax=axs, scan_path="./scan_results_POM_1000K_PtHfC", x="pressure_CH4", y="pressure_O2", z="tof",
                  gas_spec="H2", window_percent=[50, 100], window_type="time", auto_title=True)

# Adjust size of axis ticks
axs.tick_params(axis='both', which='major', labelsize=14)

# Adjust fontsize of axis labels
axs.set_xlabel(axs.get_xlabel(), fontsize=18)
axs.set_ylabel(axs.get_ylabel(), fontsize=18)

# Adjust fontsize and position of axis title
axs.set_title(axs.get_title(), fontsize=20, loc='center', pad=-170)

plt.tight_layout()
plt.savefig('CustomiseSingle.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/docs/images/plot_multiple_runs/CustomiseSingle.png?raw=true" alt="CustomiseSingle" width="500"/>
</div>

In order to customise the colorbar, one has to select `show_colorbar=False` and retrieve the colorbar instance:

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

cp = plot_heatmap(ax=axs, scan_path="./scan_results_POM_1000K_PtHfC", x="pressure_CH4", y="pressure_O2", z="tof",
                  gas_spec="H2", window_percent=[50, 100], window_type="time", auto_title=True, show_colorbar=False)

# Create colorbar and adjust the size of its tick labels
cbar = plt.colorbar(cp, ax=axs)
cbar.ax.tick_params(labelsize=14)  # Adjust the colorbar tick label size

plt.tight_layout()
plt.savefig('CustomiseColorbar.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/docs/images/plot_multiple_runs/CustomiseColorbar.png?raw=true" alt="CustomiseColorbar" width="500"/>
</div>

For a plot with a multiple heatmaps:

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

scan_path = "./scan_results_POM_1000K_PtHfC"
x = "pressure_CH4"
y = "pressure_O2"
window_percent = [50, 100]
window_type = "time"
min_molec = 10

surf_spec_values = {
    'CH3': 0.5, 'CH2': 0.5, 'CH': 0.5, 'C': 0.5, 'CH3_Pt': 0.5, 'CH2_Pt': 0.5, 'CH_Pt': 0.5, 'C_Pt': 0.5,
    'CHO': 1.5, 'CO': 2.5, 'CO_Pt': 2.5, 'COOH': 3.5, 'COOH_Pt': 3.5, 'CO2': 4.5, 'CO2_Pt': 4.5, 'H': 5.5,
    'H2O': 6.5, 'H2O_Pt': 6.5, 'OH': 7.5, 'OH_Pt': 7.5, 'O': 8.5, 'O_Pt': 8.5, 'O2_Pt': 8.5}
tick_values = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5]
tick_labels = ['$CH_{x}$', '$CHO$', '$CO$', '$COOH$', '$CO_{2}$', '$H$', '$H_{2}O$', '$OH$', '$O$']


fig, axs = plt.subplots(4, 4, figsize=(11, 9), sharey='row', sharex='col')

for n, product in enumerate(['CO', 'H2', 'H2O', 'CO2']):
    plot_heatmap(ax=axs[0, n], scan_path=scan_path, x=x, y=y, z="tof", gas_spec=product,
                 window_percent=window_percent, window_type=window_type, auto_title=True)

for n, site_type in enumerate(['tC', 'tM', 'Pt']):
    plot_heatmap(ax=axs[1, n], scan_path=scan_path, x=x, y=y, z="coverage", surf_spec="total",
                 window_percent=window_percent, window_type=window_type,
                 site_type=site_type, weights="time", auto_title=True)

for n, site_type in enumerate(['tC', 'tM', 'Pt']):
    plot_heatmap(ax=axs[2, n], scan_path=scan_path, x=x, y=y, z="phase_diagram",
                 window_percent=window_percent, window_type=window_type, site_type=site_type,
                 surf_spec_values=surf_spec_values, tick_values=tick_values, tick_labels=tick_labels,
                 min_coverage=20, weights="time", auto_title=True)

plot_heatmap(ax=axs[3, 0], scan_path=scan_path, x=x, y=y, z='selectivity', main_product="H2",
             side_products=["H2O"], window_percent=window_percent, window_type=window_type, min_molec=min_molec,
             auto_title=True)

plot_heatmap(ax=axs[3, 1], scan_path=scan_path, x=x, y=y, z='final_time', auto_title=True)

plot_heatmap(ax=axs[3, 2], scan_path=scan_path, x=x, y=y, z='energy_slope', window_percent=window_percent,
             window_type='nevents', auto_title=True)

plot_heatmap(ax=axs[3, 3], scan_path=scan_path, x=x, y=y, z='issues', window_percent=window_percent,
             auto_title=True)

# Hide empty axes:
axs[1, 3].axis('off')
axs[2, 3].axis('off')

for i in range(4):
    for j in range(4):
        # Adjust size of axis ticks
        axs[i, j].tick_params(axis='both', which='major', labelsize=12)

        # Adjust fontsize of axis labels
        axs[i, j].set_xlabel(axs[i, j].get_xlabel(), fontsize=12)
        axs[i, j].set_ylabel(axs[i, j].get_ylabel(), fontsize=12)

        # Adjust fontsize and position of axis title
        axs[i, j].set_title(axs[i, j].get_title(), fontsize=12, loc='center', pad=-110)

plt.tight_layout()
plt.savefig('CustomiseMultiple.png', dpi=200, bbox_inches='tight', transparent=False)
plt.show()
```
![CustomiseMultiple](https://github.com/hprats/ZacrosTools/blob/main/docs/images/plot_multiple_runs/CustomiseMultiple.png?raw=true)
