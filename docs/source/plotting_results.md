# Plotting results

## Plots from a single KMC simulation

Example:

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
    print("\nTOF (molec·s-1·Å-2): \n")
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

![tof_and_coverage](https://github.com/hprats/ZacrosTools/blob/main/images/tof_and_coverage.png?raw=true)

## Contour plots from a set of KMC simulations at various operating conditions

Contour plots from (*p<sub>A</sub>, p<sub>B</sub>*) or (*p<sub>A</sub>, T*) scans can be created very easy with the 
{py:func}`zacrostools.plot_functions.plot_contour` function. 

The following parameters are **mandatory**:
- **ax** (*matplotlib.axes.Axes*): Axis object where the contour plot should be created.
- **scan_path** (*str*): Path of the directory containing all the scan jobs.
- **x** (*str*): Magnitude to plot in the x-axis. Possible values: `'pressure_X'` (where `X` is a gas species) or 
`'temperature'`.
- **y** (*str*): Magnitude to plot in the y-axis. Possible values: `'pressure_Y'` (where `Y` is a gas species) or 
`'temperature'`.
- **z** (*str*): Magnitude to plot in the z-axis. Possible values: `'tof_Z'` (where `Z` is a gas species), 
`'selectivity'`, `'coverage_Z'` (where `Z` is a surface species), `'coverage_total'`, `'phase_diagram'`, `'final_time'` 
or `'final_energy'`.


Additional parameters:
- **levels** (*list*), only for tof, selectivity and coverage plots (optional). Determines the number and positions of 
the contour lines / regions. Default: `'[-3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3]'` for tof plots and 
`'[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]'` for selectivity plots.
- **min_molec** (*int*), only for tof and selectivity plots (optional). Defines a minimum number of product 
(if `z='tof_Z'`) or main_product + side_products (if `z='selectivity'` molecules in order to calculate and plot 
either the tof or the selectivity. If the number of molecules is lower, the value of tof or selectivity at that point 
will be `NaN`. If `min_molec=0`, no threshold will be applied and any value of tof lower than `min(levels)` will be 
set to that value. Default: `0`.
- **main_product** (*str*), only for selectivity plots (required). Main product to calculate the selectivity.
- **side_products** (*list*), only for selectivity plots (required). List of side products to calculate the selectivity.
- **site_type** (*str*), only for coverage and phase diagrams (optional). Name of site type. For default lattice models 
or lattice models with only one site type `site_type='default'` can be used. Default: `'default'`.
- **min_coverage** (*float*), only for phase diagrams (optional). Minimum total coverage to plot the dominant surface 
species on a phase diagram. Default: `20.0`.
- **surf_species_names** (*list*), only for phase diagrams (optional). List of surface species to include in the phase 
diagram. If `None`, all surface species will be included. Default: `None`.
- **ticks** (*list*), only for phase diagrams (optional). List of tick values for the colorbar in phase diagrams. If 
`None`, ticks are determined automatically from the input. Default: `None`.
- **ignore** (*float*) (optional). Ignore first % of simulated time, i.e., equilibration (in %). Default value: `0.0`.
- **weights** (*str*) (optional). Weights for the averages. Possible values: `'time'`, `'events'`, `None`. If `None`, 
all weights are set to 1. Default value: `None`.
- **cmap** (*str*) (optional). The colormap or instance or registered colormap name used to map scalar data to colors.
- **show_points** (*bool*) (optional). If `True`, show the grid points as black dots. Default value: `False`.

Example:

    import matplotlib.pyplot as plt
    from zacrostools.plot_functions import plot_contour
    from zacrostools.read_functions import parse_general_output

    # Parameters for the figures
    products = ['CO2', 'H2', 'CH4', 'O2']
    site_types = ['tM', 'tC']
    ignore = 30
    min_molec = 5
    x = "pressure_CO"
    y = "pressure_H2O"
    
    fig, axs = plt.subplots(3, 4, figsize=(11, 6), sharey='row', sharex='col')

    # TOF
    for n, product in enumerate(products):
        plot_contour(ax=axs[0, n], scan_path=scan_path, x=x, y=y, z=f"tof_{product}", ignore=ignore, min_molec=min_molec)

    # Total coverage
    for n, site_type in enumerate(site_types):
        plot_contour(ax=axs[1, n], scan_path=scan_path, x=x, y=y, z="coverage_total", ignore=ignore, site_type=site_type)
    
    # Phase diagrams
    for n, site_type in enumerate(site_types):
        plot_contour(ax=axs[1, n + 2], scan_path=scan_path, x=x, y=y, z="phase_diagram", ignore=ignore, site_type=site_type)
    
    # Selectivity
    plot_contour(ax=axs[2, 0], scan_path=scan_path, x=x, y=y, z='selectivity', main_product='CO2',
                 side_products=['CH4'], ignore=ignore, min_molec=min_molec)
    
    # Final simulation time
    plot_contour(ax=axs[2, 1], scan_path=scan_path, x=x, y=y, z='final_time')

    # Final simulation energy
    plot_contour(ax=axs[2, 2], scan_path=scan_path, x=x, y=y, z='final_energy')

    plt.tight_layout()
    plt.show()
    plt.savefig("/Results_scan.pdf", bbox_inches='tight', transparent=False)

![contour_plots](https://github.com/hprats/ZacrosTools/blob/main/images/contour_plots.png?raw=true)

```{warning}
This section of the documentation is under development. 
```