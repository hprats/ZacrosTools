# Reading output files

The Zacros output files can be read and stored into a KMCOutput object {py:func}`zacrostools.kmc_output.KMCOutput`, 
and then this KMCOutput can be used to extract all the simulation data and to plot results. 

## 1. Create a KMCOutput object 

A KMCOutput can be simply created by indicating the path where the output files are located:

    from zacrostools.kmc_output import KMCOutput

    kmc_output = KMCOutput(path=path_to_calculation_files)

## 2. Extract data and plot results

All KMC results can be obtained from the different {py:func}`zacrostools.kmc_output.KMCOutput` attributes.
Below there are some examples.

### Plot number of product molecules and coverage as a function of simulated time

- **Product molecules:** kmc_output.production[gas_species]  (in molec.)
- **Coverage:** kmc_output.coverage[surf_species]  (in %)

Example:

    fig, axes = plt.subplots(2, 1, figsize=(2, 4), sharex=True)

    # Number of product molecules
    for gas_species in kmc_output.gas_species_names:
        if kmc_output.tof[gas_species] > 0.0:  # products only
            axes[0].plot(kmc_output.time, kmc_output.production[gas_species], label=gas_species+'$_{(g)}$')

    # Coverage (in %)
    for surf_species in spec_sites:
        axes[1].plot(kmc_output.time, kmc_output.coverage[surf_species], label=surf_species)

### Get TOF and average coverage

- **TOF:** kmc_output.tof[gas_species]  (in molec·s^-1·Å^-2)
- **Average coverage:** kmc_output.av_coverage[surf_species]  (in %)

Example:

    # TOF (in molec·s^-1·Å^-2)
    for molecule in kmc_output.gas_species_names:
        print(f"TOF {molecule}: {kmc_output.tof[molecule]:.2e}")

    # Average coverage (in %)
    for ads in spec_sites:
        print(f"Coverage {ads}: {kmc_output.av_coverage[ads]:.2f}")

### Get selectivity

The **selectivity** can be obtained by using the method {py:meth}`zacrostools.kmc_output.KMCOutput.get_selectivity()` 
(in %)

Example:

    selectivity = kmc_output.get_selectivity(main_product='CH4', side_products=['CO2', 'CH3OH'])  # in %

### Plot contour plots (pX,pY) for TOF and selectivity

Example:
    
    list_pX_values = [0.001, 0.01, 0.1, 1.0, 10]
    list_pY_values = [0.001, 0.01, 0.1, 1.0, 10]
    tof = np.zeros((len(ylist), len(xlist)))
    selectivity = np.zeros((len(ylist), len(xlist)))

    fig, axes = plt.subplots(2, figsize=(6, 3), sharey=True)

    for i, pX in list_pX_values:
        for j, pY in list_pY_values:
            kmc_output = KMCOutput(path=f"output_{pX}_{pY}", ignore=20)
            tof[j, i] = np.log10(kmc_output.tof['CH4'])
            selectivity[j, i] = kmc_output.get_selectivity(main_product='CH4', side_products=['CO2', 'CH3OH'])

    cp = axes[0].contourf(X, Y, tof, cmap='inferno')
    plt.colorbar(cp, ax=axes[0])
    cp = axes[1].contourf(X, Y, selectivity, cmap='Greens')
    plt.colorbar(cp, ax=axes[1])

    for i in range(2):
        axes[i].set_xscale('log')
        axes[i].set_yscale('log')

### Plot kinetic phase diagram 

Example:
    
    spec_values = {'H': 0.5, 'CH3': 1.5, 'CH2': 2.5, 'CH': 3.5, 'C': 4.5, 'CO': 5.5, 'CO2': 6.5, 'O': 7.5}

    list_pX_values = [0.01, 0.1, 1.0, 10]
    list_pY_values = [0.01, 0.1, 1.0, 10]
    z = np.zeros((len(ylist), len(xlist)))

    fig, axes = plt.subplots(1, figsize=(3, 3), sharey=True)

    for i, pX in list_pX_values:
        for j, pY in list_pY_values:
            kmc_output = KMCOutput(path=f"output_{pX}_{pY}", ignore=20)
            z[j, i] = spec_values[kmc_output.dominant_ads]

    cp = axes.contourf(X, Y, z, cmap='bwr')
    plt.colorbar(cp, ax=axes)

    axes.set_xscale('log')
    axes.set_yscale('log')

```{warning}
This section of the documentation is under development. 
```