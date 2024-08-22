# Plotting Results

## Plots from a Single KMC Simulation

#### Surface coverage as a function of simulated time

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

![Coverage](https://github.com/hprats/ZacrosTools/blob/main/docs/images/Coverage.png?raw=true)

#### Molecules produced as a function of simulated time

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

![MoleculesProduced](https://github.com/hprats/ZacrosTools/blob/main/docs/images/MoleculesProduced.png?raw=true)

## Contour Plots from a Set of KMC Simulations at Various Operating Conditions

Alternatively, when running a set of KMC simulations at various operating conditions, contour plots for (*p<sub>A</sub>,
p<sub>B</sub>*) or (*p<sub>A</sub>, T*) scans can be easily created using the 
{py:func}`zacrostools.plot_functions.plot_contour` function.


### Main Parameters (**mandatory** for all plots)

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

- **levels** (*list*): Determines the number and positions of the contour lines/regions.
  - Default: `'[-3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3]'` for TOF plots.
  - Default: `'[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]'` for selectivity plots.
- **window_percent** (*list*): A list of two elements `[initial_percent, final_percent]` specifying the window of the 
total simulation. The values should be between 0 and 100, representing the percentage of the total simulated time or 
the total number of events to be considered. 
  - Default: `[0, 100]`
- **window_type** (*str*): The type of window to apply when calculating averages (e.g. av_coverage) or TOF. Possible 
values:
  - `'time'`: Apply a window over the simulated time.
  - `'nevents'`: Apply a window over the number of simulated events.
- **weights** (*str*): Weights for the averages. Possible values:
  - `'time'`
  - `'events'`
  - `None` (all weights are set to 1).
  - Default value: `None`.
- **cmap** (*str*): The colormap or instance or registered colormap name used to map scalar data to colors.
- **show_points** (*bool*): If `True`, show the grid points as black dots.
  - Default value: `False`.
- **show_colorbar** (*bool*): If `True`, show the colorbar.
  - Default value: `True`.

### Contour plot types

#### TOF

##### Additional required parameters

- **min_molec** (*int*): Defines a minimum number of product molecules to calculate and plot either the TOF or the selectivity.
  - Default: `0`.

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

![ScanTof](https://github.com/hprats/ZacrosTools/blob/main/docs/images/ScanTof.png?raw=true)

#### TOF difference

##### Additional required parameters

- **scan_path_ref** (*str*): Path of the directory containing all reference scan jobs.
  - Default: `None`.
- **min_molec** (*int*): Defines a minimum number of product molecules to calculate and plot either the TOF or the selectivity.
  - Default: `0`.

##### Example

```python
# TODO 
```

#### Selectivity

##### Additional required parameters

- **main_product** (*str*): Main product to calculate the selectivity.
- **side_products** (*list*): List of side products to calculate the selectivity.
- **min_molec** (*int*): Defines a minimum number of product molecules to calculate and plot either the TOF or the selectivity.
  - Default: `0`.

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

![ScanSelectivity](https://github.com/hprats/ZacrosTools/blob/main/docs/images/ScanSelectivity.png?raw=true)

#### Coverage

##### Additional required parameters

- **surf_spec** (*str*): Surface species for coverage plots.
  - Default: `20.0`.
- **site_type** (*str*): Name of site type.
  - Default: `'default'`.

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

![ScanCoverageTotal](https://github.com/hprats/ZacrosTools/blob/main/docs/images/ScanCoverageTotal.png?raw=true)

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

![ScanCoverageSpecific](https://github.com/hprats/ZacrosTools/blob/main/docs/images/ScanCoverageSpecific.png?raw=true)

#### Phase diagram

##### Additional required parameters

- **site_type** (*str*): Name of site type.
  - Default: `'default'`.
- **min_coverage** (*float*): Minimum total coverage to plot the dominant surface species.
  - Default: `20.0`.
- **surf_spec_values** (*list*): List of surface species to include in the phase diagram. If `None`, all surface species 
will be included. Default: `None`.
  - Default: `None`.
- **tick_values** (*list*): Ticks for the colorbar in phase diagram plots. If `None`, tick_values are determined 
automatically from the output data.
  - Default: `None`.
- **ticks_labels** (*list*): Labels for the colorbar in phase diagrams. If `None`, tick_labels are determined 
automatically from the output data.
  - Default: `None`.

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

#### Final time

##### Additional required parameters

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

#### Energy slope

##### Additional required parameters

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

#### Issues

##### Additional required parameters

##### Example

### Example with multiple contour plots

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

![Contour Plots](https://github.com/hprats/ZacrosTools/blob/main/docs/images/contour_plots.png?raw=true)

```{warning}
This section of the documentation is under development.
```
