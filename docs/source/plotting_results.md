# Plotting results

## Plotting results from a single KMC simulation

There are several ways to visualize results from a single KMC simulation. This section demonstrates how to plot surface coverage and the number of molecules produced over time.

### Plotting coverage over time

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

### Plotting the number of molecules produced

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

## Creating heatmaps from a set of KMC simulations

When running a set of KMC simulations at various operating conditions, 2D heatmaps can be created using the `plot_heatmap` function from the `zacrostools` library.

### Parameters

#### Mandatory parameters for all plot types

- **`ax`** (`matplotlib.axes.Axes`): Axis object where the contour plot should be created.
- **`scan_path`** (`str`): Path of the directory containing all the scan jobs.
- **`x`** (`str`): Magnitude to plot on the x-axis. Possible values:
  - `'pressure_X'`, where `X` is a gas species.
  - `'temperature'`.
  - `'total_pressure'`.

- **`y`** (`str`): Magnitude to plot on the y-axis. Possible values:
  - `'pressure_Y'`, where `Y` is a gas species.
  - `'temperature'`.
  - `'total_pressure'`.

- **`z`** (`str`): Magnitude to plot on the z-axis. Possible values:
  - `'tof'`: log₁₀ TOF (molec·s⁻¹·Å⁻²).
  - `'dtof'`: Difference in log₁₀ TOF between two systems.
  - `'selectivity'`: Selectivity (%).
  - `'coverage'`: Coverage (%).
  - `'phasediagram'`: Most dominant surface species.
  - `'finaltime'`: log₁₀ Final time (s).
  - `'final_energy'`: Final energy (eV·Å⁻²).
  - `'energyslope'`: Energy slope (eV·Å⁻²·step⁻¹).
  - `'issues'`: To check for issues.

Depending on the type of plot (`z`), some additional parameters might be needed (see below).

#### Optional parameters

- **`cmap`** (`str`): Colormap used to map scalar data to colors. Accepts colormap instances or registered names.
- **`show_points`** (`bool`): Displays grid points as black dots if `True`. Default is `False`.
- **`show_colorbar`** (`bool`): Displays the colorbar if `True`. Default is `True`.
- **`auto_title`** (`bool`): Automatically generates titles for subplots if `True`. Default is `False`.

### Heatmap types

#### TOF (Turnover Frequency)

`z = 'tof'`, plot the TOF (in molec·s⁻¹·Å⁻²) of a given gas-phase species.

**Additional parameters:**

Mandatory:

- **`gas_spec`** (`str`): Name of gas-phase species for the TOF calculation.

Optional:

- **`min_molec`** (`int`): Minimum product molecules for TOF calculation. Default is `0`.
- **`show_max`** (`bool`): Display a golden '*' marker at the point with the highest TOF. Default is `False`.
- **`levels`** (`list`): Specifies the contour levels for the plot. If `None`, the levels are automatically determined, with any TOF below `1.0e-06` set to this threshold. If provided, TOF values below the lowest value in levels are set to `min(levels)`. Default is `None`.
- **`analysis_range`** (`list`): Specifies the percentage range of the simulation time or events to consider. Default is `[0, 100]`.
- **`range_type`** (`str`): The type of window to apply. Default is `'time'`. Possible values:
  - `'time'` (based on simulated time)
  - `'nevents'` (based on the number of events)

**Example:**

```python
import numpy as np
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

plot_heatmap(
    ax=axs,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
    z='tof',
    gas_spec='H2',
    min_molec=0,
    analysis_range=[50, 100],
    range_type='time',
    levels=np.logspace(-1, 4, num=11),
    auto_title=True,
    show_points=False,
    show_colorbar=True
)

plt.tight_layout()
plt.savefig('tof_heatmap.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/tof_heatmap.png?raw=true" alt="TOF heatmap" width="500"/> </div>

#### TOF difference

`z = 'dtof'`, plot the TOF difference (∆TOF, in molec·s⁻¹·Å⁻²) of a given gas-phase species between two simulations.

**Additional parameters:**

Mandatory:

- **`gas_spec`** (`str`): Name of gas-phase species for the TOF calculation.
- **`scan_path_ref`** (`str`): Path to the directory containing reference scan job results.

Optional:

- **`levels`** (`list`): Defines the levels used in the colorbar. If `None`, the levels are automatically determined based on the data, with TOF differences below `1.0e-06` set to this value. If `levels` is provided, any TOF difference below the smallest value in levels is set to `min(levels)`. Default is `None`.
- **`analysis_range`** (`list`): Percentage range of the simulation time or events to consider. Default is `[0, 100]`.
- **`range_type`** (`str`): Type of window to apply. Default is `'time'`. Possible values:
  - `'time'` (based on simulated time)
  - `'nevents'` (based on the number of events)

**Note:** The `min_molec` parameter is not allowed in `z = 'dtof'` plots.

**Example:**

```python
import numpy as np
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

plot_heatmap(
    ax=axs,
    scan_path='simulation_results',
    scan_path_ref='simulation_results_reference',
    x='pressure_CH4',
    y='pressure_CO2',
    z='dtof',
    gas_spec='H2',
    min_molec=0,
    analysis_range=[50, 100],
    range_type='time',
    levels=np.logspace(-1, 4, num=11),
    auto_title=True,
    show_points=False,
    show_colorbar=True
)

plt.tight_layout()
plt.savefig('dtof_heatmap.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/dtof_heatmap.png?raw=true" alt="∆TOF heatmap" width="500"/> </div>

#### Selectivity

`z = 'selectivity'`, plot the selectivity (in %) towards a given gas-phase species.

**Additional parameters:**

Mandatory:

- **`main_product`** (`str`): The main product for selectivity calculation.
- **`side_products`** (`list`): List of side products for selectivity calculation.

Optional:

- **`min_molec`** (`int`): Minimum value of main + side product molecules for selectivity calculation. Default is `None`.
- **`levels`** (`list`): Defines the levels used in the colorbar. Default is `np.linspace(0, 100, 11, dtype=int)`.
- **`analysis_range`** (`list`): Percentage range of the simulation time or events to consider. Default is `[0, 100]`.
- **`range_type`** (`str`): Type of window to apply. Default is `'time'`. Possible values:
  - `'time'` (based on simulated time)
  - `'nevents'` (based on the number of events)

**Example:**

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

plot_heatmap(
    ax=axs,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
    z='selectivity',
    main_product='H2',
    side_products=['H2O'],
    min_molec=100,
    analysis_range=[50, 100],
    range_type='time',
    auto_title=True,
    show_points=False,
    show_colorbar=True
)

plt.tight_layout()
plt.savefig('selectivity_heatmap.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/selectivity_heatmap.png?raw=true" alt="Selectivity heatmap" width="500"/> </div>

#### Coverage

`z = 'coverage'`, plot the coverage (in %) of one or all surface species.

**Additional parameters:**

Mandatory:

- **`surf_spec`** (`str`): Surface species for coverage plots. Use `'total'` for total coverage.

Optional:

- **`site_type`** (`str`): Name of site type. Default is `'default'`.
- **`levels`** (`list`): Defines the levels used in the colorbar. Default is `np.linspace(0, 100, 11, dtype=int)`.
- **`analysis_range`** (`list`): Percentage range of the simulation time or events to consider. Default is `[0, 100]`.
- **`range_type`** (`str`): Type of window to apply. Default is `'time'`. Possible values:
  - `'time'` (based on simulated time)
  - `'nevents'` (based on the number of events)
- **`weights`** (`str`): Weights for the averages. Default is `None`. Possible values:
  - `'time'`
  - `'nevents'`
  - `None` (all weights are set to 1)

**Example (total coverage):**

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

plot_heatmap(
    ax=axs,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
    z='coverage',
    surf_spec="total",
    site_type='tC',
    analysis_range=[50, 100],
    range_type='time',
    weights='time',
    auto_title=True,
    show_points=False,
    show_colorbar=True
)

plt.tight_layout()
plt.savefig('coverage_heatmap.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/coverage_heatmap.png?raw=true" alt="Coverage heatmap" width="500"/> </div>

#### Phase diagram

`z = 'phasediagram'`, plot the most dominant surface species.

**Additional parameters:**

Optional:

- **`site_type`** (`str`): Name of the site type. Default is `'default'`.
- **`min_coverage`** (`float`): Minimum total coverage required to plot the dominant surface species. Default is `20.0`.
- **`surf_spec_values`** (`dict`): Dictionary mapping surface species to numerical values. If `None`, all species are included. Default is `None`.
- **`tick_values`** (`list`): Tick marks for the colorbar. If `None`, they are determined automatically. Default is `None`.
- **`tick_labels`** (`list`): Labels for the colorbar ticks. If `None`, they are determined automatically. Default is `None`.
- **`analysis_range`** (`list`): Percentage range of the simulation time or events to consider. Default is `[0, 100]`.
- **`range_type`** (`str`): Type of window to apply. Default is `'time'`.
- **`weights`** (`str`): Weights for averaging. Default is `None`.

**Example:**

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

plot_heatmap(
    ax=axs,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
    z='phasediagram',
    min_coverage=50.0,
    site_type='tC',
    surf_spec_values={
        'CH3': 0.5, 'CH3_Pt': 0.5, 'CH2': 0.5, 'CH2_Pt': 0.5, 'CH': 0.5, 'CH_Pt': 0.5, 'C': 0.5,
        'C_Pt': 0.5,
        'CHO': 1.5, 'CHO_Pt': 1.5, 'COH': 1.5, 'COH_Pt': 1.5,
        'CO': 2.5, 'CO_Pt': 2.5,
        'COOH': 3.5, 'COOH_Pt': 3.5,
        'CO2': 4.5, 'CO2_Pt': 4.5,
        'H': 5.5, 'H_Pt': 5.5,
        'H2O': 6.5, 'H2O_Pt': 6.5,
        'OH': 7.5, 'OH_Pt': 7.5,
        'O': 8.5, 'O_Pt': 8.5
    },
    tick_values=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5],
    tick_labels=['$CH_{x}$', '$CHO/COH$', '$CO$', '$COOH$', '$CO_{2}$', '$H$', '$H_{2}O$', '$OH$', '$O$'],
    analysis_range=[50, 100],
    range_type='time',
    weights='time',
    auto_title=True,
    show_points=False,
    show_colorbar=True
)

plt.tight_layout()
plt.savefig('phasediagram_heatmap.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/phasediagram_heatmap.png?raw=true" alt="Phase diagram heatmap" width="500"/> </div>

#### Final time

`z = 'finaltime'`, plot the final time of the simulation (in s).

**Additional parameters:**

Optional:

- **`levels`** (`list`): Defines the levels used in the colorbar. If `None`, levels are automatically determined from the plot. Default is `None`.

**Example:**

```python
import numpy as np
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

plot_heatmap(
    ax=axs,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
    z='finaltime',
    levels=np.logspace(-5, 7, num=13),
    verbose=True,
    auto_title=True,
    show_points=False,
    show_colorbar=True
)

plt.tight_layout()
plt.savefig('finaltime_heatmap.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/finaltime_heatmap.png?raw=true" alt="Final time heatmap" width="500"/> </div>

#### Energy slope

`z = 'energyslope'`, plot the slope of the lattice energy (in eV·Å⁻²·step⁻¹).

A high slope of the lattice energy indicates that the simulation might have not reached the steady state.

**Additional parameters:**

Optional:

- **`levels`** (`list`): Defines the levels used in the colorbar. Default is `np.logspace(-11, -8, num=7)`.
- **`analysis_range`** (`list`): Percentage range of the simulation time or events to consider. Default is `[50, 100]`.
- **`range_type`** (`str`): Type of window to apply. Default is `'nevents'`.

**Example:**

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

plot_heatmap(
    ax=axs,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
    z='energyslope',
    range_type='nevents',
    auto_title=True,
    show_points=False,
    show_colorbar=True
)

plt.tight_layout()
plt.savefig('energyslope_heatmap.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/energyslope_heatmap.png?raw=true" alt="Energy slope heatmap" width="500"/> </div>

#### Simulation issues

To identify and visualize potential issues in simulations, set `z = 'issues'`. This plot displays a colored mesh that highlights simulations with detected problems.

**Issue detection criteria:**

1. **Trend analysis**: Positive or negative trends in lattice energy within the selected events window.
2. **Non-linearity**: Deviations from linearity in the time vs. number of events plot within the selected events window.

These issues often arise from simulations that are too short (i.e., the system has not reached steady state) or problems with the dynamic scaling algorithm. Be aware that false positives or negatives can occur, so manual verification of results is recommended.

**Additional required parameters:**

- **`analysis_range`** (`list`): A list of two elements `[initial_percent, final_percent]` specifying the window of the total simulation. The values should be between 0 and 100, representing the percentage of the total simulated time or the total number of events to be considered. Default is `[30, 100]`.

**Example:**

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

plot_heatmap(
    ax=axs,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
    z='issues',
    verbose=True,
    auto_title=True,
    show_points=False,
    show_colorbar=True
)

plt.tight_layout()
plt.savefig('issues_heatmap.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/issues_heatmap.png?raw=true" alt="Issues heatmap" width="500"/> </div>

### Multiple types of plots

Different types of heatmaps can be combined in a single figure, as shown in the following example:

```python
import numpy as np
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

# Plot parameters
scan_path = 'simulation_results'
x_variable = 'pressure_CH4'
y_variable = 'pressure_CO2'

analysis_range = [50, 100]  # (in %) Ignore first X% of total simulated time (equilibration)
range_type = 'time'
weights = 'time'

min_molec_tof = 0  # To plot TOF and selectivity
min_molec_selectivity = 100  # To plot TOF and selectivity
min_coverage = 50  # (in %) To plot phase diagrams

auto_title = True
show_points = False
show_colorbar = True

fig, axs = plt.subplots(4, 3, figsize=(8.8, 8), sharey='row', sharex='col')

for n, product in enumerate(['CO', 'H2', 'H2O']):
    plot_heatmap(
        ax=axs[0, n], scan_path=scan_path, x=x_variable, y=y_variable, z="tof",
        gas_spec=product, min_molec=min_molec_tof,
        analysis_range=analysis_range, range_type=range_type, levels=np.logspace(-1, 4, num=11),
        auto_title=auto_title, show_points=show_points, show_colorbar=show_colorbar)

for n, site_type in enumerate(['tC', 'tM', 'Pt']):
    plot_heatmap(
        ax=axs[1, n], scan_path=scan_path, x=x_variable, y=y_variable, z="coverage",
        surf_spec="total", site_type=site_type,
        analysis_range=analysis_range, range_type=range_type, weights=weights,
        auto_title=auto_title, show_points=show_points, show_colorbar=show_colorbar)

for n, site_type in enumerate(['tC', 'tM', 'Pt']):
    plot_heatmap(
        ax=axs[2, n], scan_path=scan_path, x=x_variable, y=y_variable, z="phasediagram",
        min_coverage=min_coverage, site_type=site_type,
        surf_spec_values={
            'CH3': 0.5, 'CH3_Pt': 0.5, 'CH2': 0.5, 'CH2_Pt': 0.5, 'CH': 0.5, 'CH_Pt': 0.5, 'C': 0.5,
            'C_Pt': 0.5,
            'CHO': 1.5, 'CHO_Pt': 1.5, 'COH': 1.5, 'COH_Pt': 1.5,
            'CO': 2.5, 'CO_Pt': 2.5,
            'COOH': 3.5, 'COOH_Pt': 3.5,
            'CO2': 4.5, 'CO2_Pt': 4.5,
            'H': 5.5, 'H_Pt': 5.5,
            'H2O': 6.5, 'H2O_Pt': 6.5,
            'OH': 7.5, 'OH_Pt': 7.5,
            'O': 8.5, 'O_Pt': 8.5
        },
        tick_values=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5],
        tick_labels=['$CH_{x}$', '$CHO/COH$', '$CO$', '$COOH$', '$CO_{2}$', '$H$', '$H_{2}O$', '$OH$', '$O$'],
        analysis_range=analysis_range, range_type=range_type, weights=weights,
        auto_title=auto_title, show_points=show_points, show_colorbar=show_colorbar)

plot_heatmap(
    ax=axs[3, 0], scan_path=scan_path, x=x_variable, y=y_variable, z='selectivity',
    main_product='H2', side_products=['H2O'], min_molec=min_molec_selectivity,
    analysis_range=analysis_range, range_type=range_type,
    auto_title=auto_title, show_points=show_points, show_colorbar=show_colorbar)

plot_heatmap(
    ax=axs[3, 1], scan_path=scan_path, x=x_variable, y=y_variable, z='finaltime',
    levels=np.logspace(-7, 7, num=15), auto_title=auto_title, show_points=show_points, show_colorbar=show_colorbar)

# Hide axis labels of intermediate subplots
for i in range(3):
    for j in range(3):
        axs[i, j].set_xlabel('')
for i in range(3):
    for j in range(1, 3):
        axs[i, j].set_ylabel('')

# Hide blank subplots
axs[3, 2].axis('off')

plt.tight_layout()
plt.savefig('multiple_heatmaps.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/multiple_heatmaps.png?raw=true" alt="Multiple heatmaps" width="700"/> </div>

### Customizing the plots

The size of axis ticks and font size of axis labels and titles can be adjusted with Matplotlib. Below are examples that show how to do that.

**For a plot with a single heatmap:**

```python
import numpy as np
import matplotlib.pyplot as plt
from zacrostools.plot_functions import plot_heatmap

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

cp = plot_heatmap(
    ax=axs,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
    z='tof',
    gas_spec='H2',
    min_molec=0,
    analysis_range=[50, 100],
    range_type='time',
    levels=np.logspace(-1, 4, num=11),
    auto_title=True,
    show_points=False,
    show_colorbar=False
)

# Adjust size of axis ticks
axs.tick_params(axis='both', which='major', labelsize=14)

# Adjust font size of axis labels
axs.set_xlabel(axs.get_xlabel(), fontsize=18)
axs.set_ylabel(axs.get_ylabel(), fontsize=18)

# Adjust font size and position of axis title
axs.set_title(axs.get_title(), fontsize=20, loc='center', pad=-170)

# Create colorbar and adjust the size of its tick labels
cbar = plt.colorbar(cp, ax=axs)
cbar.ax.tick_params(labelsize=14)  # Adjust the colorbar tick label size

plt.tight_layout()
plt.savefig('tof_heatmap_custom.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/tof_heatmap_custom.png?raw=true" alt="TOF heatmap custom" width="500"/> </div>


## Note on axis options

The `x` and `y` parameters accept `'total_pressure'` as an option in addition to `'pressure_X'` and `'temperature'`. When `'total_pressure'` is selected, the total pressure of the system is plotted on that axis using a logarithmic scale, similar to partial pressures.

