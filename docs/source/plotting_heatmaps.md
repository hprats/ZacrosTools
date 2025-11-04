# Plotting heatmaps

The following specialized functions are available to generate heatmap plots from large parameter scans:

- `plot_tof` – Turnover frequency of a gas-phase species
- `plot_dtof` – Difference in TOF w.r.t. a reference scan (absolute or relative)
- `plot_selectivity` – Selectivity (%) of a main product vs side products
- `plot_coverage` – Coverage (%) of surface species on a site type (or total coverage)
- `plot_phasediagram` – Dominant surface species phase map
- `plot_finaltime` – Final simulated time (s)
- `plot_energyslope` – Energy slope (|dE/d(step)| per area per step)
- `plot_issues` – Yes/No map of runs with detected issues

#### Common parameters

These following parameters are available in most heatmap types:
- **`ax`** (`matplotlib.axes.Axes`): Matplotlib axis to draw on.
- **`x`**, **`y`** (`str`): Names of the scan dimensions. If the name contains `"pressure"`, that axis is set to logarithmic scale and tick values are converted from log10 to absolute units for plotting.
- **`scan_path`** (`str`): Path to the directory holding one subfolder per operating point.
- **`cmap`** (`str`, *optional*): Matplotlib colormap name. Defaults vary by plot (see below).
- **`show_points`** (`bool`, *optional*): Overlay white dots at each grid node (default = `False`).
- **`show_colorbar`** (`bool`, *optional*): Draw a colorbar (default = `True`).
- **`auto_title`** (`bool`, *optional*): Add title (default = `False`).
- **`analysis_range`** (`list[float]`, *optional*): Percentage window of the simulation data to analyze (default = `[0, 100]`).
- **`range_type`** (`str`, *optional*): `'time'` for simulated time windows or `'nevents'` for number-of-events windows (default = `'time'`).
- **`weights`** (`str`, *optional*): Averaging weights passed to `KMCOutput`. Possible values: `'time'`, `'events'`, or `None` (default = `'None'`).

---

#### TOF

Parameters specific to `plot_tof`:
- **`gas_spec`** (`str`): Gas species key (e.g., `'H2'`, `'CO'`).
- **`min_molec`** (`int`, *optional*): Minimum total production required for a valid TOF (default = `1`).
- **`levels`** (`list` or `ndarray`, *optional*): Contour levels to use in the plot.
- **`show_max`** (`bool`, *optional*): Mark the global maximum with a golden `*` (default = `False`).

```python
import numpy as np
import matplotlib.pyplot as plt
from zacrostools.heatmaps.tof import plot_tof

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))
plot_tof(
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
    show_colorbar=True
)
plt.tight_layout()
plt.savefig('tof_heatmap.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/tof_heatmap.png?raw=true" alt="TOF heatmap" width="500"/> </div>


#### TOF difference 

Parameters specific to `plot_dtof`:
- **`difference_type`** (`str`):  
  - `'absolute'`: ∆TOF = TOF(main) − TOF(ref)  
  - `'relative'`: ∆TOF = (TOF(main) - TOF(ref)) / TOF(ref) * 100
  - `'ratio'`: ∆TOF = |TOF(main) / TOF(ref)|
- **`scale`** (`str`, *optional*): `'log'` uses `LogNorm` or `'lin'` (only available for `difference_type='absolute'`).
- **`nlevels`** (`int`, *optional*): Number of discrete color levels. 
- **`min_tof_ref`** (`float`, *optional*): Mask cells whose reference TOF is below this threshold (default = `0`).
- **`check_issues`** (`str`, *optional*): run `detect_issues` on `'none'`, `'main'`, `'ref'`, or `'both'`; flagged cells are masked.

```python
import numpy as np
import matplotlib.pyplot as plt
from zacrostools.heatmaps.dtof import plot_dtof

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))
plot_dtof(
    ax=axs,
    scan_path='simulation_results',
    scan_path_ref='simulation_results_reference',
    x='pressure_CH4',
    y='pressure_CO2',
    gas_spec='H2',
    difference_type='absolute',
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

Parameters specific to `plot_selectivity`:
- **`main_product`** (`str`) and **`side_products`** (`list[str]`, required).
- **`min_molec`** (`int`, *optional*): Minimum **combined** production (main + sides) to accept the value (default = `0`).
- **`levels`** (`list` or `ndarray`, *optional*): Contour levels to use in the plot.

```python
import matplotlib.pyplot as plt
from zacrostools.heatmaps.selectivity import plot_selectivity

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))
plot_selectivity(
    ax=axs,
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

#### Coverage

Parameters specific to `plot_coverage`:
- **`surf_spec`** (`str` or `list`): Surface species for which coverage is calculated. Use `'all'` to plot total coverage.
- **`site_type`** (`str`, *optional*): Site type to consider (default = `'StTp1'`).

```python
import matplotlib.pyplot as plt
from zacrostools.heatmaps.coverage import plot_coverage

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))
plot_coverage(
    ax=axs,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
    surf_spec='all',
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

Parameters specific to `plot_phasediagram`:
- **`site_type`** (`str`, *optional*): Site type to consider (default = `'StTp1'`).
- **`min_coverage`** (`float` or `int`, *optional*): Minimum total coverage (%) to consider a dominant species (default = `50.0`).
- **`tick_labels`** (`dict` or `None`, *optional*): Mapping of colorbar tick labels to lists of surface species.

```python
import matplotlib.pyplot as plt
from zacrostools.heatmaps.phasediagram import plot_phasediagram

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))
tick_labels = {  # for phase diagram plots
    '$CH_{x}$': ['CH3*', 'CH3_Pt*', 'CH2*', 'CH2_Pt*', 'CH*', 'CH_Pt*', 'C*', 'C_Pt*'],
    '$CHO/COH$': ['CHO*', 'CHO_Pt*', 'COH*', 'COH_Pt*'],
    '$CO$': ['CO*', 'CO_Pt*'],
    '$COOH$': ['COOH*', 'COOH_Pt*'],
    '$CO_{2}$': ['CO2*', 'CO2_Pt*'],
    '$H$': ['H*', 'H_Pt*'],
    '$H_{2}O$': ['H2O*', 'H2O_Pt*'],
    '$OH$': ['OH*', 'OH_Pt*'],
    '$O$': ['O*', 'O_Pt*'],
}
plot_phasediagram(
    ax=axs,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
    min_coverage=50.0,
    site_type='tC',
    tick_labels=tick_labels,
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

Parameters specific to `plot_finaltime`:
- **`levels`** (`list` or `ndarray`, *optional*): Contour levels to use in the plot.

```python
import numpy as np
import matplotlib.pyplot as plt
from zacrostools.heatmaps.finaltime import plot_finaltime

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))
plot_finaltime(
    ax=axs,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
    levels=np.logspace(-5, 7, num=13),
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

Parameters specific to `plot_energyslope`:
- **`levels`** (`list` or `ndarray`, *optional*): Contour levels to use in the plot.

```python
import matplotlib.pyplot as plt
from zacrostools.heatmaps.energyslope import plot_energyslope

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))
plot_energyslope(
    ax=axs,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
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

#### Issues

Parameters specific to `plot_issues`:
- **`energy_slope_thr`** (`float`, *optional*): Absolute energy-slope threshold (default = `5.0e-10`).
- **`time_r2`** (`float`, *optional*): Minimum acceptable R² for linearity of time vs events (default = `0.95`).
- **`max_points`** (`int`, *optional*): Maximum number of sampled points used inside `detect_issues` for the diagnostics (default = `100`).
- **`verbose`** (`bool`, *optional*): If `True`, prints paths of simulations with detected issues (default = `False`).

```python
import matplotlib.pyplot as plt
from zacrostools.heatmaps.issues import plot_issues

fig, axs = plt.subplots(1, figsize=(4.3, 3.5))
plot_issues(
    ax=axs,
    scan_path='simulation_results',
    x='pressure_CH4',
    y='pressure_CO2',
    analysis_range=[50, 100],
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

---

#### Building a multi-panel figure

You can combine multiple heatmaps into a single figure. Below is a compact example with 4 rows × 3 columns using a common scan and consistent analysis window.

```python
import numpy as np
import matplotlib.pyplot as plt
from zacrostools.heatmaps.tof import plot_tof
from zacrostools.heatmaps.dtof import plot_dtof
from zacrostools.heatmaps.selectivity import plot_selectivity
from zacrostools.heatmaps.coverage import plot_coverage
from zacrostools.heatmaps.phasediagram import plot_phasediagram
from zacrostools.heatmaps.finaltime import plot_finaltime

# Plot parameters
scan_path = 'simulation_results'
x_variable = 'pressure_CH4'
y_variable = 'pressure_CO2'

analysis_range = [50, 100]      # Ignore first 50 % of total simulated time (equilibration)
range_type = 'time'
weights = 'time'

min_molec_tof = 0               # For TOF and selectivity
min_molec_selectivity = 100     # For TOF and selectivity
min_coverage = 50               # (in %) To plot phase diagrams

auto_title = True
show_points = False
show_colorbar = True

# Define labels for phase diagram heatmaps
tick_labels = { 
    '$CH_{x}$': ['CH3*', 'CH3_Pt*', 'CH2*', 'CH2_Pt*', 'CH*', 'CH_Pt*', 'C*', 'C_Pt*'],
    '$CHO/COH$': ['CHO*', 'CHO_Pt*', 'COH*', 'COH_Pt*'],
    '$CO$': ['CO*', 'CO_Pt*'],
    '$COOH$': ['COOH*', 'COOH_Pt*'],
    '$CO_{2}$': ['CO2*', 'CO2_Pt*'],
    '$H$': ['H*', 'H_Pt*'],
    '$H_{2}O$': ['H2O*', 'H2O_Pt*'],
    '$OH$': ['OH*', 'OH_Pt*'],
    '$O$': ['O*', 'O_Pt*'],
}

fig, axs = plt.subplots(4, 3, figsize=(8.8, 8), sharey='row', sharex='col')

for n, product in enumerate(['CO', 'H2', 'H2O']):
    plot_tof(
        ax=axs[0, n], scan_path=scan_path, x=x_variable, y=y_variable,
        gas_spec=product, min_molec=min_molec_tof,
        analysis_range=analysis_range, range_type=range_type, levels=np.logspace(-1, 4, num=11),
        auto_title=auto_title, show_points=show_points, show_colorbar=show_colorbar)

for n, site_type in enumerate(['tC', 'tM', 'Pt']):
    plot_coverage(
        ax=axs[1, n], scan_path=scan_path, x=x_variable, y=y_variable,
        surf_spec='all', site_type=site_type,
        analysis_range=analysis_range, range_type=range_type, weights=weights,
        auto_title=auto_title, show_points=show_points, show_colorbar=show_colorbar)

for n, site_type in enumerate(['tC', 'tM', 'Pt']):
    plot_phasediagram(
        ax=axs[2, n], scan_path=scan_path, x=x_variable, y=y_variable,
        min_coverage=min_coverage, site_type=site_type, tick_labels=tick_labels,
        analysis_range=analysis_range, range_type=range_type, weights=weights,
        auto_title=auto_title, show_points=show_points, show_colorbar=show_colorbar)

plot_selectivity(
    ax=axs[3, 0], scan_path=scan_path, x=x_variable, y=y_variable,
    main_product='H2', side_products=['H2O'], min_molec=min_molec_selectivity,
    analysis_range=analysis_range, range_type=range_type,
    auto_title=auto_title, show_points=show_points, show_colorbar=show_colorbar)

plot_finaltime(
    ax=axs[3, 1], scan_path=scan_path, x=x_variable, y=y_variable,
    levels=np.logspace(-7, 7, num=15), auto_title=auto_title, show_points=show_points, show_colorbar=show_colorbar)

plot_dtof(
    ax=axs[3, 2], scan_path=scan_path, x=x_variable, y=y_variable,
    scan_path_ref='simulation_results_reference', gas_spec='H2', min_molec=0, levels=np.logspace(-1, 4, num=11),
    analysis_range=analysis_range, range_type=range_type,
    auto_title=auto_title, show_points=show_points, show_colorbar=show_colorbar)

# Hide axis labels of intermediate subplots
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

#### Customizing text sizes and colorbars

You can adjust tick sizes, label fonts, and title placement using standard Matplotlib APIs. Example for a single TOF subplot:

```python
import numpy as np
import matplotlib.pyplot as plt
from zacrostools.heatmaps.tof import plot_tof

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
# Adjust font size and position of axis title
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

---
