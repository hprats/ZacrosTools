# Plotting Results

## Simple Plots from a Single KMC Simulation

### Example

```python
import matplotlib.pyplot as plt
from zacrostools.kmc_output import KMCOutput

kmc_output = KMCOutput(path='.', ignore=0.0, weights='time')

fig, axes = plt.subplots(2, 1, figsize=(3, 6), sharex=True)

# Plot surface coverage
print("\nSurface coverage (%, per site type): \n")
for site_type in kmc_output.site_types:
    for surf_species in kmc_output.coverage_per_site_type[site_type]:
        coverage = kmc_output.av_coverage_per_site_type[site_type][surf_species]
        print(f"{surf_species}*: {coverage:.3f} % of {site_type} sites")
        if coverage >= 1.0:
            axes[0].plot(kmc_output.time, kmc_output.coverage_per_site_type[site_type][surf_species],
                         label=f"{surf_species} ({site_type})")

# Plot TOF
print("\nTOF (molec·s⁻¹·Å⁻²): \n")
for gas_species in kmc_output.gas_species_names:
    print(f"{gas_species}: {kmc_output.tof[gas_species]:.3e}")
    if kmc_output.tof[gas_species] > 0.0 and kmc_output.production[gas_species][-1] > 0:
        axes[1].plot(kmc_output.time, kmc_output.production[gas_species],
                     linewidth=2, label=gas_species + '$_{(g)}$')

for ax in axes:
    ax.legend()
axes[0].set_ylabel('Coverage (%)')
axes[1].set_ylabel('Molecules')
axes[1].set_xlabel('Time (s)')
plt.tight_layout()
plt.show()
```

![TOF and Coverage Plot](https://github.com/hprats/ZacrosTools/blob/main/docs/images/tof_and_coverage.png?raw=true)

## Contour Plots from a Set of KMC Simulations at Various Operating Conditions

Contour plots from (*p<sub>A</sub>, p<sub>B</sub>*) or (*p<sub>A</sub>, T*) scans can be easily created using the {py:func}`zacrostools.plot_functions.plot_contour` function.

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
  - `'tof_Z'`, where `Z` is a gas species
  - `'tof_difference_Z'`, where `Z` is a gas species
  - `'selectivity'`
  - `'coverage_Z'`, where `Z` is a surface species
  - `'coverage_total'`
  - `'phase_diagram'`
  - `'final_time'`
  - `'final_energy'`

### Additional Parameters

- **levels** (*list*): Determines the number and positions of the contour lines/regions.
  - Default: `'[-3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3]'` for TOF plots.
  - Default: `'[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]'` for selectivity plots.
- **min_molec** (*int*): Defines a minimum number of product molecules to calculate and plot either the TOF or the selectivity.
  - Default: `0`.
- **scan_path_ref** (*str*): Path of the directory containing all reference scan jobs (only required for toff 
difference plots).
  - Default: `None`.
- **main_product** (*str*, required for selectivity plots): Main product to calculate the selectivity.
- **side_products** (*list*, required for selectivity plots): List of side products to calculate the selectivity.
- **site_type** (*str*): Name of site type for coverage and phase diagrams.
  - Default: `'default'`.
- **min_coverage** (*float*): Minimum total coverage to plot the dominant surface species on a phase diagram.
  - Default: `20.0`.
- **surf_spec_values** (*list*): List of surface species to include in the phase diagram. If `None`, all surface species 
will be included. Default: `None`.
  - Default: `None`.
- **tick_values** (*list*): Ticks for the colorbar in phase diagram plots. If `None`, tick_values are determined 
automatically from the output data.
  - Default: `None`.
- **tick_values** (*list*): List of tick values for the colorbar in phase diagrams. If `None`, ticks are determined 
automatically from the input. 
  - Default: `None`.
- **ticks_labels** (*list*): Labels for the colorbar in phase diagrams. If `None`, tick_labels are determined 
automatically from the output data.
  - Default: `None`.
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

### Example

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
