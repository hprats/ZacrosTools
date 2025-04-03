# Plotting heatmaps

When running a set of KMC simulations at various operating conditions, 2D heatmaps can be created using various specialized `plot_X` functions such as `plot_tof` or `plot_selectivity`.

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

Depending on the type of plot, some additional parameters might be needed (see below).

#### Optional parameters

- **`cmap`** (`str`): Colormap used to map scalar data to colors. Accepts colormap instances or registered names.  
  **Default**: depends on the function.
- **`show_points`** (`bool`): Displays grid points as black dots if `True`.  
  **Default**: `False`.
- **`show_colorbar`** (`bool`): Displays the colorbar if `True`.  
  **Default**: `True`.
- **`auto_title`** (`bool`): Automatically generates titles for subplots if `True`.  
  **Default**: `False`.

### Heatmap types

#### TOF (Turnover Frequency)

Plot the TOF (in molec·s⁻¹·Å⁻²) of a given gas-phase species.

**Additional parameters:**

Mandatory:

- **`gas_spec`** (`str`): Name of the gas-phase species for the TOF difference calculation.

Optional:

- **`min_molec`** (`int`): Minimum total production in both main and reference simulations to consider the result valid.  
  **Default**: `1`.
- **`weights`** (`str`): Weights for the averages. Possible values:
  - `'time'`
  - `'events'`
  - `None` (all weights are set to 1)  
  **Default**: `None`.
- **`levels`** (`list` or `np.ndarray`): Contour levels to use in the plot. When provided, TOF values are clipped to the minimum and maximum values in this list.
- **`analysis_range`** (`list`): Portion of the simulation data to analyze.  
  **Default**: `[0, 100]`.
- **`range_type`** (`str`): The type of window to apply. Possible values:
  - `'time'` (based on simulated time)
  - `'nevents'` (based on the number of events)  
  **Default**: `'time'`.
- **`show_max`** (`bool`): Display a golden `'*'` marker at the point with the highest TOF.  
  **Default**: `False`.

**Example:**

```python
import numpy as np
import matplotlib.pyplot as plt
from zacrostools.plot_functions.tof import plot_tof

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

plot_tof(
    ax=axs,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
    gas_spec='H2',
    # Changed default is now 1, but we can override as needed:
    min_molec=0,
    # analysis_range is used to specify which portion of the simulation to analyze:
    analysis_range=[50, 100],
    range_type='time',
    # If levels are not provided, the function auto-scales the TOF data:
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

#### ∆TOF (Delta TOF)

Plot the difference in Turnover Frequencies (TOF) between a main simulation and a reference simulation for a specified gas-phase species. The difference can be either *absolute* (`main - reference`) or *relative* (percentage difference).

**Additional parameters:**

Mandatory:

- **`gas_spec`** (`str`): Name of the gas-phase species for the TOF difference calculation.
- **`scan_path_ref`** (`str`): Path to the reference simulation directories.

Optional:

- **`difference_type`** (`str`): Type of TOF difference to compute. Must be either `'absolute'` or `'relative'`.  
  **Default**: `'absolute'`.
- **`scale`** (`str`): Determines the color scaling of the difference. Possible values:
  - `'log'`
  - `'lin'`  
  **Default**: `'log'`.
- **`min_molec`** (`int`): Minimum total production in both main and reference simulations to consider the result valid.  
  **Default**: `1`.
- **`max_dtof`** (`float`): Maximum absolute value for \(\Delta\)TOF. For relative differences, the default is 100. If provided, values above (or below the negative) limit are clipped.
- **`min_dtof`** (`float`): Threshold that defines the smallest nonzero \(\Delta\)TOF to display. By default, it’s set automatically (depending on `max_dtof`).
- **`nlevels`** (`int`): Number of discrete boundaries if you want to segment the \(\Delta\)TOF scale.  
  - `0`: use continuous normalization.  
  - Must be a positive odd integer (`>=3`) for discrete normalization.  
  **Default**: `0`.
- **`weights`** (`str`): Weights for the averages. Possible values:
  - `'time'`
  - `'events'`
  - `None` (all weights are set to 1)  
  **Default**: `None`.
- **`analysis_range`** (`list`): Portion of the simulation data to analyze.  
  **Default**: `[0, 100]`.
- **`range_type`** (`str`): The type of window to apply. Possible values:
  - `'time'`
  - `'nevents'`  
  **Default**: `'time'`.

**Example:**

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions.dtof import plot_dtof

fig, ax = plt.subplots(1, figsize=(4.3, 3.5))

plot_dtof(
    ax=ax,
    scan_path='simulation_results',
    scan_path_ref='reference_results',
    x='pressure_CH4',
    y='pressure_CO2',
    gas_spec='H2',
    difference_type='absolute',
    scale='log',
    min_molec=0,
    nlevels=11,
    analysis_range=[50, 100],
    range_type='time',
    auto_title=True,
    show_points=False,
    show_colorbar=True
)

plt.tight_layout()
plt.savefig('dtof_heatmap.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/dtof_heatmap.png?raw=true" alt="∆TOF heatmap" width="500"/> </div>

#### Selectivity (%)

Plot the selectivity (in %) of a **main product** with respect to one or more **side products**.

**Additional parameters:**

Mandatory:

- **`main_product`** (`str`): Name of the main product for the selectivity calculation.
- **`side_products`** (`list`): List of side products for the selectivity calculation.

Optional:

- **`min_molec`** (`int`): Minimum combined production (main + side products) required for a valid selectivity value.  
  **Default**: `1`.
- **`weights`** (`str`): Weights for the averages. Possible values:
  - `'time'`
  - `'events'`
  - `None` (all weights are set to 1)  
  **Default**: `None`.
- **`levels`** (`list` or `np.ndarray`): Contour levels to use in the plot (e.g., `np.linspace(0, 100, 11, dtype=int)`). If provided, selectivity values are clipped to the minimum and maximum values in this list.  
  **Default**: `np.linspace(0, 100, 11, dtype=int)`.
- **`analysis_range`** (`list`): Portion of the simulation data to analyze.  
  **Default**: `[0, 100]`.
- **`range_type`** (`str`): The type of window to apply. Possible values:
  - `'time'`
  - `'nevents'`  
  **Default**: `'time'`.
- **`cmap`** (`str`): Colormap used to map scalar data to colors.  
  **Default**: `'Greens'`.

**Example:**

```python
import numpy as np
import matplotlib.pyplot as plt
from zacrostools.plot_functions.selectivity import plot_selectivity

fig, ax = plt.subplots(1, figsize=(4.3, 3.5))

plot_selectivity(
    ax=ax,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
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

#### Coverage (%)

Plot the coverage (in %) of specified surface species (or total coverage) on a given site type.

**Additional parameters:**

Mandatory:

- **`surf_spec`** (`str` or `list`): Surface species to include in the coverage calculation.  
  - `'all'`: Total coverage (of all adsorbates) is shown.  
  - A single species name (`'CO*'`) or a list of species (`['CH*', 'C*']`) can also be provided.

Optional:

- **`site_type`** (`str`): The site type on which coverage is computed.  
  **Default**: `'default'`.
- **`weights`** (`str`): Weights for the averages. Possible values:
  - `'time'`
  - `'events'`
  - `None` (all weights are set to 1)  
  **Default**: `None`.
- **`levels`** (`list` or `np.ndarray`): Contour levels to use in the plot (e.g., `np.linspace(0, 100, 11, dtype=int)`). If provided, coverage values are clipped to the minimum and maximum values in this list.  
  **Default**: `np.linspace(0, 100, 11, dtype=int)`.
- **`analysis_range`** (`list`): Portion of the simulation data to analyze.  
  **Default**: `[0, 100]`.
- **`range_type`** (`str`): The type of window to apply. Possible values:
  - `'time'`
  - `'nevents'`  
  **Default**: `'time'`.
- **`cmap`** (`str`): Colormap used to map scalar data to colors.  
  **Default**: `'Oranges'`.

**Example:**

```python
import numpy as np
import matplotlib.pyplot as plt
from zacrostools.plot_functions.coverage import plot_coverage

fig, ax = plt.subplots(1, figsize=(4.3, 3.5))

plot_coverage(
    ax=ax,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
    surf_spec='all',
    site_type='tC',
    weights='time',
    analysis_range=[50, 100],
    range_type='time',
    auto_title=True,
    show_points=False,
    show_colorbar=True
)

plt.tight_layout()
plt.savefig('coverage_heatmap.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/coverage_heatmap.png?raw=true" alt="Coverage heatmap" width="500"/> </div>

#### Phase Diagram

Plot a phase diagram where each point is assigned a **dominant surface species** (or `NaN` if coverage is too low). The color encodes these dominant species, grouped according to user-provided or auto-generated labels.

**Additional parameters:**

*(No additional mandatory parameters are required.)*

Optional:

- **`site_type`** (`str`): Site type to consider when retrieving the dominant surface species.  
  **Default**: `'default'`.
- **`min_coverage`** (`float` or `int`): Minimum coverage threshold (%) for a species to be considered dominant.  
  **Default**: `50.0`.
- **`tick_labels`** (`dict`): Custom mapping for species grouping and colorbar labels. The keys are used as colorbar labels (e.g., `'$CH_{x}$'`), and the values are lists of species names (e.g., `['CH3', 'CH2', 'C']`). When not provided, the function automatically parses a `simulation_input.dat` file from the first simulation directory to assign each species to its own group.
- **`weights`** (`str`): Weights for the averages. Possible values:
  - `'time'`
  - `'events'`
  - `None` (all weights are set to 1)  
  **Default**: `None`.
- **`analysis_range`** (`list`): Portion of the simulation data to analyze.  
  **Default**: `[0, 100]`.
- **`range_type`** (`str`): The type of window to apply. Possible values:
  - `'time'`
  - `'nevents'`  
  **Default**: `'time'`.

**Example:**

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions.phasediagram import plot_phasediagram

tick_labels = {  
    '$CH_{x}$': ['CH3', 'CH3_Pt', 'CH2', 'CH2_Pt', 'CH',
                 'CH_Pt', 'C', 'C_Pt'],
    '$CHO/COH$': ['CHO', 'CHO_Pt', 'COH', 'COH_Pt'],
    '$CO$': ['CO', 'CO_Pt'],
    '$COOH$': ['COOH', 'COOH_Pt'],
    '$CO_{2}$': ['CO2', 'CO2_Pt'],
    '$H$': ['H', 'H_Pt'],
    '$H_{2}O$': ['H2O', 'H2O_Pt'],
    '$OH$': ['OH', 'OH_Pt'],
    '$O$': ['O', 'O_Pt']
}

fig, ax = plt.subplots(1, figsize=(4.3, 3.5))

plot_phasediagram(
    ax=ax,
    scan_path='simulation_results',
    x='pressure_CO2',
    y='pressure_CH4',
    site_type='tC',
    min_coverage=50.0,
    tick_labels=tick_labels,
    weights='time',
    analysis_range=[50, 100],
    range_type='time',
    auto_title=True,
    show_points=False,
    show_colorbar=True
)

plt.tight_layout()
plt.savefig('phase_diagram.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/phasediagram_heatmap.png?raw=true" alt="Phase diagram heatmap" width="500"/> </div>

#### Final Time (s)

Plot the **final simulation time** (in seconds) for each job in a 2D heatmap. The color scale is logarithmically normalized.

**Additional parameters:**

*(No additional mandatory parameters are required.)*

Optional:

- **`levels`** (`list` or `np.ndarray`): Contour levels for the plot. If provided, final time values are clipped to the minimum and maximum in this list.  
  **Default**: `None`.

**Example:**

```python
import numpy as np
import matplotlib.pyplot as plt
from zacrostools.plot_functions.finaltime import plot_finaltime

fig, ax = plt.subplots(1, figsize=(4.3, 3.5))

plot_finaltime(
    ax=ax,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
    levels=np.logspace(-5, 7, num=13),
    show_points=False,
    show_colorbar=True,
    auto_title=True
)

plt.tight_layout()
plt.savefig('finaltime_heatmap.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/finaltime_heatmap.png?raw=true" alt="Final time heatmap" width="500"/> </div>

#### Energy Slope

Plot the **energy slope** computed during the KMC simulation in a 2D heatmap. By default, data are shown on a logarithmic scale (using `LogNorm`).

**Additional parameters:**

*(No additional mandatory parameters are required.)*

Optional:

- **`levels`** (`list` or `np.ndarray`): Levels for normalization. If provided, the color scale is clipped between `min(levels)` and `max(levels)`.  
  **Default**: `np.logspace(-11, -8, num=7)`.
- **`analysis_range`** (`list`): Portion of the simulation data to analyze.  
  **Default**: `[0, 100]`.
- **`range_type`** (`str`): The dimension considered in the analysis. Possible values:
  - `'time'`
  - `'nevents'`  
  **Default**: `'time'`.

**Example:**

```python
import matplotlib.pyplot as plt
import numpy as np
from zacrostools.plot_functions.energyslope import plot_energyslope

fig, ax = plt.subplots(1, figsize=(4.3, 3.5))

plot_energyslope(
    ax=ax,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
    analysis_range=[50, 100],
    range_type='time',
    auto_title=True,
    show_points=False,
    show_colorbar=True
)

plt.tight_layout()
plt.savefig('energyslope_heatmap.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/energyslope_heatmap.png?raw=true" alt="Energy slope heatmap" width="500"/> </div>

#### Issues

Check each simulation for **issues** and visualize the results in a yes/no heatmap.

**Additional parameters:**

Mandatory:

- **`analysis_range`** (`list`): Portion of the simulation data to analyze (e.g., `[0, 100]`). If `None`, it is internally set to `[0, 100]`.

Optional:

- **`range_type`** (`str`): The dimension used for slicing the simulation data. Possible values:
  - `'time'`
  - `'nevents'`  
  **Default**: `'time'`.
- **`cmap`** (`str`): Colormap used for plotting.  
  **Default**: `'RdYlGn'`.
- **`verbose`** (`bool`): If `True`, prints the paths of simulations that contain issues.  
  **Default**: `False`.

**Example:**

```python
import matplotlib.pyplot as plt
from zacrostools.plot_functions.issues import plot_issues

fig, ax = plt.subplots(1, figsize=(4.3, 3.5))

plot_issues(
    ax=ax,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
    analysis_range=[50, 100],
    range_type='time',
    verbose=True,
    auto_title=True,
    show_colorbar=True,
    show_points=False
)

plt.tight_layout()
plt.savefig('issues_heatmap.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/issues_heatmap.png?raw=true" alt="Issues heatmap" width="500"/> </div>

### Figure with multiple heatmaps

Different specialized plotting functions can be combined in a single figure, as illustrated below. Each function (`plot_tof`, `plot_coverage`, `plot_phasediagram`, `plot_selectivity`, `plot_finaltime`, etc.) handles a particular type of heatmap.

```python
import numpy as np
import matplotlib.pyplot as plt

# Import the specialized plotting functions
from zacrostools.plot_functions.tof import plot_tof
from zacrostools.plot_functions.coverage import plot_coverage
from zacrostools.plot_functions.phasediagram import plot_phasediagram
from zacrostools.plot_functions.selectivity import plot_selectivity
from zacrostools.plot_functions.finaltime import plot_finaltime

# General parameters
scan_path = 'simulation_results'
x_variable = 'pressure_CH4'
y_variable = 'pressure_CO2'

analysis_range = [50, 100]  # (in %) Ignore first X% of the total simulated time (e.g., initial equilibration)
range_type = 'time'
weights = 'time'

min_molec_tof = 0
min_molec_selectivity = 100
min_coverage = 50  # (in %) Minimum coverage threshold for phase diagrams

auto_title = True
show_points = False
show_colorbar = True

fig, axs = plt.subplots(4, 3, figsize=(8.8, 8), sharey='row', sharex='col')

# --- First row: TOF for different products ---
for n, product in enumerate(['CO', 'H2', 'H2O']):
    plot_tof(
        ax=axs[0, n],
        scan_path=scan_path,
        x=x_variable,
        y=y_variable,
        gas_spec=product,
        min_molec=min_molec_tof,
        analysis_range=analysis_range,
        range_type=range_type,
        levels=np.logspace(-1, 4, num=11),
        auto_title=auto_title,
        show_points=show_points,
        show_colorbar=show_colorbar
    )

# --- Second row: Coverage for different site types ---
for n, site_type in enumerate(['tC', 'tM', 'Pt']):
    plot_coverage(
        ax=axs[1, n],
        scan_path=scan_path,
        x=x_variable,
        y=y_variable,
        surf_spec='all',
        site_type=site_type,
        analysis_range=analysis_range,
        range_type=range_type,
        weights=weights,
        auto_title=auto_title,
        show_points=show_points,
        show_colorbar=show_colorbar
    )

# --- Third row: Phase diagram for different site types ---
# Example grouping of species into labeled categories for the colorbar
tick_labels = {
    '$CH_{x}$': ['CH3', 'CH3_Pt', 'CH2', 'CH2_Pt', 'CH', 'CH_Pt', 'C', 'C_Pt'],
    '$CHO/COH$': ['CHO', 'CHO_Pt', 'COH', 'COH_Pt'],
    '$CO$': ['CO', 'CO_Pt'],
    '$COOH$': ['COOH', 'COOH_Pt'],
    '$CO_{2}$': ['CO2', 'CO2_Pt'],
    '$H$': ['H', 'H_Pt'],
    '$H_{2}O$': ['H2O', 'H2O_Pt'],
    '$OH$': ['OH', 'OH_Pt'],
    '$O$': ['O', 'O_Pt']
}

for n, site_type in enumerate(['tC', 'tM', 'Pt']):
    plot_phasediagram(
        ax=axs[2, n],
        scan_path=scan_path,
        x=x_variable,
        y=y_variable,
        site_type=site_type,
        min_coverage=min_coverage,
        tick_labels=tick_labels,
        analysis_range=analysis_range,
        range_type=range_type,
        auto_title=auto_title,
        show_points=show_points,
        show_colorbar=show_colorbar
    )

# --- Fourth row: Selectivity and Final Time ---
# Selectivity
plot_selectivity(
    ax=axs[3, 0],
    scan_path=scan_path,
    x=x_variable,
    y=y_variable,
    main_product='H2',
    side_products=['H2O'],
    min_molec=min_molec_selectivity,
    analysis_range=analysis_range,
    range_type=range_type,
    auto_title=auto_title,
    show_points=show_points,
    show_colorbar=show_colorbar
)

# Final time
plot_finaltime(
    ax=axs[3, 1],
    scan_path=scan_path,
    x=x_variable,
    y=y_variable,
    levels=np.logspace(-7, 7, num=15),
    auto_title=auto_title,
    show_points=show_points,
    show_colorbar=show_colorbar
)

# Hide the third subplot in the last row
axs[3, 2].axis('off')

# Optional: clean up labels in intermediate subplots
for i in range(3):
    for j in range(3):
        axs[i, j].set_xlabel('')
for i in range(3):
    for j in range(1, 3):
        axs[i, j].set_ylabel('')

plt.tight_layout()
plt.savefig('multiple_heatmaps.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;"> 
  <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/multiple_heatmaps.png?raw=true" alt="Multiple heatmaps" width="700"/> 
</div>

---

### Customization

The size of axis ticks and font size of axis labels and titles can be adjusted with Matplotlib. Below is an example (shown here for a single heatmap, but the same approach applies to multi-plot figures as well):

```python
import numpy as np
import matplotlib.pyplot as plt
from zacrostools.plot_functions.tof import plot_tof

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))

cp = plot_tof(
    ax=axs,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
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

# Adjust font size and position of the title
axs.set_title(axs.get_title(), fontsize=20, loc='center', pad=-170)

# Create colorbar and adjust the size of its tick labels
cbar = plt.colorbar(cp, ax=axs)
cbar.ax.tick_params(labelsize=14)

plt.tight_layout()
plt.savefig('tof_heatmap_custom.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;"> 
  <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/tof_heatmap_custom.png?raw=true" alt="TOF heatmap custom" width="500"/>
</div>
```