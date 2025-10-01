# Plotting heatmaps

This guide documents the heatmap plotting helpers in `zacrostools.heatmaps`. These functions build 2D heatmaps from batches of Zacros KMC jobs arranged under a **scan directory**. Each subfolder in the scan represents one operating point (e.g., a specific pair of partial pressures or temperature/pressure).

The following specialized functions are available:

- `plot_tof` – Turnover frequency of a gas-phase species
- `plot_dtof` – Difference in TOF w.r.t. a reference scan (absolute or relative)
- `plot_selectivity` – Selectivity (%) of a main product vs side products
- `plot_coverage` – Coverage (%) of surface species on a site type (or total coverage)
- `plot_phasediagram` – Dominant surface species phase map
- `plot_finaltime` – Final simulated time (s)
- `plot_energyslope` – Energy slope (|dE/d(step)| per area per step)
- `plot_issues` – Yes/No map of runs with detected issues

All functions take **x** and **y** names that correspond to how your scan encodes the operating variables in folder names (e.g., `pressure_CO2=…`, `temperature=…`, `total_pressure=…`). If the axis name contains the substring **`"pressure"`**, the corresponding axis is plotted in **log-scale** automatically; otherwise it is in linear scale. Axis labels are formatted via `heatmap_functions.get_axis_label`.

> **Tip.** Use `show_points=True` to overlay the simulation grid nodes on top of the heatmap, and `auto_title=True` to auto-generate a bold, high-contrast title bar.

---

## Common parameters

These appear (with identical meaning) in all plotting functions unless stated otherwise.

- **`ax`** (`matplotlib.axes.Axes`, required): Matplotlib axis to draw on.
- **`x`**, **`y`** (`str`, required): Names of the scan dimensions. If the name contains `"pressure"`, that axis is set to logarithmic scale and tick values are converted from log10 to absolute units for plotting.
- **`scan_path`** (`str`, required): Path to the directory holding one subfolder per operating point.
- **`cmap`** (`str`, optional): Matplotlib colormap name. Defaults vary by plot (see below).
- **`show_points`** (`bool`, default `False`): Overlay white dots at each grid node.
- **`show_colorbar`** (`bool`, default `True`): Draw a colorbar.
- **`auto_title`** (`bool`, default `False`): Render an automatic, styled subplot title.

### About analysis windows and weights

Several plots read time series and accept:

- **`analysis_range`** (`list[float]`, default `[0, 100]`): Percentage window of the simulation data to analyze.
- **`range_type`** (`str`, default `'time'`): `'time'` for simulated time windows or `'nevents'` for number-of-events windows.
- **`weights`** (`str` or `None`): Averaging weights passed to `KMCOutput` (`'time'`, `'events'`, or `None`).

---

## TOF (Turnover Frequency): `plot_tof`

**What it shows:** TOF of a gas-phase species (molec·s⁻¹·Å⁻²). Values are plotted with **logarithmic normalization** (`LogNorm`).

```python
from zacrostools.heatmaps.tof import plot_tof
```

### Parameters specific to TOF

- **`gas_spec`** (`str`, required): Gas species key (e.g., `'H2'`, `'CO'`).
- **`min_molec`** (`int`, default `1`): Minimum total production required for a valid TOF.
- **`levels`** (`list`/`ndarray` or `None`): If provided, TOF values are clipped to `[min(levels), max(levels)]` and those become `LogNorm` bounds.
- **`show_max`** (`bool`, default `False`): Mark the global maximum with a golden `*`.

### Example

```python
import numpy as np, matplotlib.pyplot as plt
from zacrostools.heatmaps.tof import plot_tof

fig, ax = plt.subplots(figsize=(4.6, 3.6))
cp = plot_tof(
    ax=ax,
    scan_path="simulation_results",
    x="pressure_CH4",
    y="pressure_CO2",
    gas_spec="H2",
    min_molec=1,
    analysis_range=[50, 100],
    range_type="time",
    levels=np.logspace(-1, 4, 11),
    show_max=True,
    auto_title=True,
    show_points=False,
    show_colorbar=True,
)
plt.tight_layout()
plt.savefig("tof_heatmap.png", dpi=300, bbox_inches="tight")
plt.show()
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/tof_heatmap.png?raw=true" alt="TOF heatmap" width="500"/> </div>

---

## ∆TOF (Delta TOF): `plot_dtof`

**What it shows:** Difference in TOF between a **main** scan (`scan_path`) and a **reference** scan (`scan_path_ref`). Supports absolute or relative differences, optional percentage format, and optional masking of simulations with issues via `detect_issues`. Uses **continuous** or **discrete** normalization, linear or logarithmic, with sign-correct behavior (via `SymLogNorm` when needed).

```python
from zacrostools.heatmaps.dtof import plot_dtof
```

### Key behaviors & parameters

- **`difference_type`**:  
  - `'absolute'`: ∆TOF = TOF(main) − TOF(ref)  
  - `'relative'`: ∆TOF = (TOF(main) − TOF(ref)) / |TOF(ref)|; with **`percent=True`**, values are in %.
- **`scale`**: `'log'` uses `LogNorm` (all positive/negative) or `SymLogNorm` (mixed sign); `'lin'` uses linear normalization.
- **`nlevels`**: `0` → continuous normalization; odd ≥3 → discrete bins (`BoundaryNorm`). For `'log'`, bins are log-spaced (mirrored about 0).
- **`min_tof_ref`** (`float`, default `0.0`): Mask cells whose reference TOF is below this threshold.
- **`check_issues`**: run `detect_issues` on `'none'`, `'main'`, `'ref'`, or `'both'`; flagged cells are masked.
- **Color range**: Symmetric about zero. If `max_dtof`/`min_dtof` not set, sensible defaults are chosen per mode.

### Example: absolute, continuous log scale

```python
import matplotlib.pyplot as plt
from zacrostools.heatmaps.dtof import plot_dtof

fig, ax = plt.subplots(figsize=(4.6, 3.6))
cp = plot_dtof(
    ax=ax,
    scan_path="simulation_results",
    scan_path_ref="reference_results",
    x="pressure_CH4",
    y="pressure_CO2",
    gas_spec="H2",
    difference_type="absolute",
    scale="log",
    min_molec=1,
    nlevels=0,              # continuous
    analysis_range=[50, 100],
    range_type="time",
    check_issues="none",
    auto_title=True,
    show_points=False,
    show_colorbar=True,
)
plt.tight_layout()
plt.savefig("dtof_heatmap.png", dpi=300, bbox_inches="tight")
plt.show()
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/dtof_heatmap.png?raw=true" alt="∆TOF heatmap" width="500"/> </div>

---

## Selectivity (%): `plot_selectivity`

**What it shows:** Selectivity of a **main product** against specified **side products**, in percent. Values are clipped to the provided `levels` (linear scale).

```python
from zacrostools.heatmaps.selectivity import plot_selectivity
```

### Parameters specific to Selectivity

- **`main_product`** (`str`, required) and **`side_products`** (`list[str]`, required).
- **`min_molec`** (`int`): Minimum **combined** production (main + sides) to accept the value.
- **`levels`**: The plotted range is `[min(levels), max(levels)]`.

### Example

```python
import matplotlib.pyplot as plt, numpy as np
from zacrostools.heatmaps.selectivity import plot_selectivity

fig, ax = plt.subplots(figsize=(4.6, 3.6))
cp = plot_selectivity(
    ax=ax,
    scan_path="simulation_results",
    x="pressure_CH4",
    y="pressure_CO2",
    main_product="H2",
    side_products=["H2O"],
    min_molec=100,
    analysis_range=[50, 100],
    range_type="time",
    levels=np.linspace(0, 100, 11, dtype=int),
    cmap="Greens",
    auto_title=True,
)
plt.tight_layout()
plt.savefig("selectivity_heatmap.png", dpi=300, bbox_inches="tight")
plt.show()
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/selectivity_heatmap.png?raw=true" alt="Selectivity heatmap" width="500"/> </div>

---

## Coverage (%): `plot_coverage`

**What it shows:** Coverage on a **site type** for either a list of adsorbates (summed) or `'all'` (total coverage). Values are clipped to `levels` (linear scale).

```python
from zacrostools.heatmaps.coverage import plot_coverage
```

### Parameters specific to Coverage

- **`surf_spec`** (`'all'` | `str` | `list[str]`): `'all'` means total coverage. A string or list sums the listed adsorbates’ coverages.
- **`site_type`** (`str`, default `'default'`).

### Example

```python
import matplotlib.pyplot as plt
from zacrostools.heatmaps.coverage import plot_coverage

fig, ax = plt.subplots(figsize=(4.6, 3.6))
cp = plot_coverage(
    ax=ax,
    scan_path="simulation_results",
    x="pressure_CH4",
    y="pressure_CO2",
    surf_spec="all",
    site_type="tC",
    weights="time",
    analysis_range=[50, 100],
    range_type="time",
    auto_title=True,
    show_points=False,
    show_colorbar=True,
)
plt.tight_layout()
plt.savefig("coverage_heatmap.png", dpi=300, bbox_inches="tight")
plt.show()
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/coverage_heatmap.png?raw=true" alt="Coverage heatmap" width="500"/> </div>

---

## Phase Diagram (dominant adsorbate): `plot_phasediagram`

**What it shows:** For each operating point, the **dominant surface species** on a chosen site type, provided total coverage ≥ `min_coverage`. Species (or groups of species) are mapped to numeric bins and rendered with `pcolormesh`. The colorbar tick labels are the **keys** of `tick_labels` (strings like `$CH_{x}$`), and each label corresponds to a list of surface species names in that group.

```python
from zacrostools.heatmaps.phasediagram import plot_phasediagram
```

### Parameters specific to Phase Diagram

- **`site_type`** (`str`, default `'default'`).
- **`min_coverage`** (`float|int`, default `50.0`): Minimum total coverage (%) to consider a dominant species.
- **`tick_labels`** (`dict` or `None`): `{label_str: [species, ...], ...}`.  
  If `None`, the code parses `simulation_input.dat` from the first simulation and assigns **each species to its own group** (label=species). The function validates that provided species exist in the simulation; if you accidentally pass `'O'` while only `'O*'` exists, a helpful error is raised.

### Example

```python
import matplotlib.pyplot as plt

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

fig, ax = plt.subplots(figsize=(4.6, 3.6))
cp = plot_phasediagram(
    ax=ax,
    scan_path="simulation_results",
    x="pressure_CO2",
    y="pressure_CH4",
    site_type="tC",
    min_coverage=50.0,
    tick_labels=tick_labels,
    weights="time",
    analysis_range=[50, 100],
    range_type="time",
    auto_title=True,
    show_points=False,
    show_colorbar=True,
)
plt.tight_layout()
plt.savefig("phase_diagram.png", dpi=300, bbox_inches="tight")
plt.show()
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/phasediagram_heatmap.png?raw=true" alt="Phase diagram heatmap" width="500"/> </div>

---

## Final Time (s): `plot_finaltime`

**What it shows:** The final simulation time read from each job. Plotted with **logarithmic normalization** (`LogNorm`).

```python
from zacrostools.heatmaps.finaltime import plot_finaltime
```

### Parameters specific to Final Time

- **`levels`** (`list`/`ndarray` or `None`): If provided, sets `LogNorm(vmin=min(levels), vmax=max(levels))`; otherwise auto-normalized.

### Example

```python
import numpy as np, matplotlib.pyplot as plt
from zacrostools.heatmaps.finaltime import plot_finaltime

fig, ax = plt.subplots(figsize=(4.6, 3.6))
cp = plot_finaltime(
    ax=ax,
    scan_path="simulation_results",
    x="pressure_CH4",
    y="pressure_CO2",
    levels=np.logspace(-5, 7, 13),
    auto_title=True,
    show_points=False,
    show_colorbar=True,
)
plt.tight_layout()
plt.savefig("finaltime_heatmap.png", dpi=300, bbox_inches="tight")
plt.show()
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/finaltime_heatmap.png?raw=true" alt="Final time heatmap" width="500"/> </div>

---

## Energy Slope: `plot_energyslope`

**What it shows:** The **energy slope** metric gathered from each run (as computed via `KMCOutput`). Rendered with `pcolormesh` and `LogNorm`.

```python
from zacrostools.heatmaps.energyslope import plot_energyslope
```

### Parameters specific to Energy Slope

- **`levels`**: If provided, `LogNorm(vmin=min(levels), vmax=max(levels))`; otherwise auto-normalized.

### Example

```python
import matplotlib.pyplot as plt
from zacrostools.heatmaps.energyslope import plot_energyslope

fig, ax = plt.subplots(figsize=(4.6, 3.6))
cp = plot_energyslope(
    ax=ax,
    scan_path="simulation_results",
    x="pressure_CH4",
    y="pressure_CO2",
    analysis_range=[50, 100],
    range_type="time",
    auto_title=True,
    show_points=False,
    show_colorbar=True,
)
plt.tight_layout()
plt.savefig("energyslope_heatmap.png", dpi=300, bbox_inches="tight")
plt.show()
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/energyslope_heatmap.png?raw=true" alt="Energy slope heatmap" width="500"/> </div>

---

## Issues (Yes/No): `plot_issues`

**What it shows:** For each run, whether **issues** are detected by `zacrostools.detect_issues.detect_issues` within the selected analysis window. Rendered via `pcolormesh` with a centered 2-bin scale: `-0.5 → "Yes"`, `+0.5 → "No"`.

```python
from zacrostools.heatmaps.issues import plot_issues
```

### Parameters specific to Issues

- **`analysis_range`** (`list`, required): If `None`, the function internally sets `[0, 100]`.
- **Pass-through thresholds**: `energy_slope_thr`, `time_r2_thr`, `max_points` forwarded to `detect_issues`.
- **`verbose`**: If `True`, prints paths of simulations with detected issues.

### Example

```python
import matplotlib.pyplot as plt
from zacrostools.heatmaps.issues import plot_issues

fig, ax = plt.subplots(figsize=(4.6, 3.6))
cp = plot_issues(
    ax=ax,
    scan_path="simulation_results",
    x="pressure_CH4",
    y="pressure_CO2",
    analysis_range=[50, 100],
    range_type="time",
    verbose=True,
    auto_title=True,
    show_colorbar=True,
    show_points=False,
)
plt.tight_layout()
plt.savefig("issues_heatmap.png", dpi=300, bbox_inches="tight")
plt.show()
```

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/issues_heatmap.png?raw=true" alt="Issues heatmap" width="500"/> </div>

---

## Building a multi-panel figure

You can combine multiple heatmaps into a single figure. Below is a compact example with 4 rows × 3 columns using a common scan and consistent analysis window.

```python
import numpy as np
import matplotlib.pyplot as plt

from zacrostools.heatmaps.tof import plot_tof
from zacrostools.heatmaps.coverage import plot_coverage
from zacrostools.heatmaps.phasediagram import plot_phasediagram
from zacrostools.heatmaps.selectivity import plot_selectivity
from zacrostools.heatmaps.finaltime import plot_finaltime

scan_path = "simulation_results"
x_variable = "pressure_CH4"
y_variable = "pressure_CO2"

analysis_range = [50, 100]
range_type = "time"
weights = "time"

min_molec_tof = 1
min_molec_selectivity = 100
min_coverage = 50

auto_title = True
show_points = False
show_colorbar = True

fig, axs = plt.subplots(4, 3, figsize=(8.8, 8), sharey="row", sharex="col")

# Row 1: TOF of three products
for n, product in enumerate(["CO", "H2", "H2O"]):
    plot_tof(
        ax=axs[0, n],
        scan_path=scan_path,
        x=x_variable,
        y=y_variable,
        gas_spec=product,
        min_molec=min_molec_tof,
        analysis_range=analysis_range,
        range_type=range_type,
        levels=np.logspace(-1, 4, 11),
        auto_title=auto_title,
        show_points=show_points,
        show_colorbar=show_colorbar,
    )

# Row 2: Total coverage on three site types
for n, site_type in enumerate(["tC", "tM", "Pt"]):
    plot_coverage(
        ax=axs[1, n],
        scan_path=scan_path,
        x=x_variable,
        y=y_variable,
        surf_spec="all",
        site_type=site_type,
        analysis_range=analysis_range,
        range_type=range_type,
        weights=weights,
        auto_title=auto_title,
        show_points=show_points,
        show_colorbar=show_colorbar,
    )

# Row 3: Phase diagram on three site types
tick_labels = {
    "$CH_{x}$": ["CH3", "CH3_Pt", "CH2", "CH2_Pt", "CH", "CH_Pt", "C", "C_Pt"],
    "$CHO/COH$": ["CHO", "CHO_Pt", "COH", "COH_Pt"],
    "$CO$": ["CO", "CO_Pt"],
    "$COOH$": ["COOH", "COOH_Pt"],
    "$CO_{2}$": ["CO2", "CO2_Pt"],
    "$H$": ["H", "H_Pt"],
    "$H_{2}O$": ["H2O", "H2O_Pt"],
    "$OH$": ["OH", "OH_Pt"],
    "$O$": ["O", "O_Pt"],
}

for n, site_type in enumerate(["tC", "tM", "Pt"]):
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
        show_colorbar=show_colorbar,
    )

# Row 4: Selectivity and Final time (leave last cell empty)
plot_selectivity(
    ax=axs[3, 0],
    scan_path=scan_path,
    x=x_variable,
    y=y_variable,
    main_product="H2",
    side_products=["H2O"],
    min_molec=min_molec_selectivity,
    analysis_range=analysis_range,
    range_type=range_type,
    auto_title=auto_title,
    show_points=show_points,
    show_colorbar=show_colorbar,
)

plot_finaltime(
    ax=axs[3, 1],
    scan_path=scan_path,
    x=x_variable,
    y=y_variable,
    levels=np.logspace(-7, 7, 15),
    auto_title=auto_title,
    show_points=show_points,
    show_colorbar=show_colorbar,
)

axs[3, 2].axis("off")

# Optional cosmetic cleanup
for i in range(3):
    for j in range(3):
        axs[i, j].set_xlabel("")
for i in range(3):
    for j in range(1, 3):
        axs[i, j].set_ylabel("")

plt.tight_layout()
plt.savefig("multiple_heatmaps.png", dpi=300, bbox_inches="tight")
plt.show()
```

<div style="text-align: center;"> 
  <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/multiple_heatmaps.png?raw=true" alt="Multiple heatmaps" width="700"/> 
</div>

---

## Customizing text sizes and colorbars

You can adjust tick sizes, label fonts, and title placement using standard Matplotlib APIs. Example for a single TOF subplot:

```python
import numpy as np, matplotlib.pyplot as plt
from zacrostools.heatmaps.tof import plot_tof

fig, ax = plt.subplots(figsize=(4.3, 3.5))
cp = plot_tof(
    ax=ax,
    scan_path="simulation_results",
    x="pressure_CH4",
    y="pressure_CO2",
    gas_spec="H2",
    min_molec=1,
    analysis_range=[50, 100],
    range_type="time",
    levels=np.logspace(-1, 4, 11),
    auto_title=True,
    show_colorbar=False,
)

# Adjust size of axis ticks
ax.tick_params(axis="both", which="major", labelsize=14)

# Adjust font size of axis labels
ax.set_xlabel(ax.get_xlabel(), fontsize=18)
ax.set_ylabel(ax.get_ylabel(), fontsize=18)

# Adjust font size and position of the title
ax.set_title(ax.get_title(), fontsize=20, loc="center", pad=-170)

# Create colorbar and adjust the size of its tick labels
cbar = plt.colorbar(cp, ax=ax)
cbar.ax.tick_params(labelsize=14)

plt.tight_layout()
plt.savefig("tof_heatmap_custom.png", dpi=300, bbox_inches="tight")
plt.show()
```

<div style="text-align: center;"> 
  <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/tof_heatmap_custom.png?raw=true" alt="TOF heatmap custom" width="500"/>
</div>

---

## Notes & error handling

- If a simulation subfolder cannot be parsed, the corresponding cell is set to **NaN** (and left blank in the plot), with a warning printed.
- When a grid node (x,y) is missing entirely from the scan directory, a warning is emitted and a NaN is assigned.
- If duplicated (x,y) values are found (multiple folders encode the same pair), a `PlotError` is raised to protect data integrity.
- `plot_tof` and `plot_selectivity` use **`contourf`**; `plot_dtof`, `plot_energyslope`, `plot_phasediagram`, and `plot_issues` use **`pcolormesh`**; `plot_finaltime` uses **`contourf`**. Normalization choices are described in each section above.

