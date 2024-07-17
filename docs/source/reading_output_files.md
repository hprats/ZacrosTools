# Reading output files

## 1. Store simulation data in a `KMCOutput` object

All the information about a finished Zacros simulation can be extracted by creating a `KMCOutput` object 
{py:func}`zacrostools.kmc_output.KMCOutput`.

Example:

    from zacrostools.kmc_output import KMCOutput

    kmc_output = KMCOutput(path='zacros_results', ignore=30.0)

### Arguments

**Mandatory:**
- **path** (*str*): Path of the directory containing the output files

**Optional:**
- **ignore** (*float*): Ignore first % of the total simulated time (in %). This keyword is used to ignore the data from 
the equilibration phase when computing the averages. Default value: `0.0` 
- **weights** (*str*). Weights for the averages. Possible values: `'time'`, `'events'`, `None`. If `None`, 
all weights are set to 1. Default value: `None`.

## 2. Read simulation data from a `KMCOutput` object

All KMC results can be obtained from the different `KMCOutput` attributes.

### General simulation data
- **n_gas_species** (*int*): Number of gas species.
- **gas_species_names** (*list of str*): Gas species names.
- **n_surf_species** (*int*): Number of surface species.
- **surf_species_names** (*list of str*): Surface species names.
- **n_sites** (*int*): Total number of lattice sites.
- **area** (*float*): Lattice surface area (in Å^2).
- **site_types** (*dict*): Site type names and total number of sites of that type.

### Simulated time
- **time** (*np.Array*): Simulated time (in s).
- **final_time** (*float*): Final simulated time (in s).

### Lattice energy
- **energy** (*np.Array*): Lattice energy (in eV·Å^-2).
- **av_energy** (*float*): Average lattice energy (in eV·Å^-2).
- **final_energy** (*float*): Final lattice energy (in eV·Å^-2).

### Molecules consumed/produced and TOF
- **production** (*dict*): Gas species produced. Example: `KMCOutput.production['CO']`
- **total_production** (*dict*): Total number of gas species produced. Example: `KMCOutput.total_production['CO']`
- **tof** (*dict*): TOF of gas species (in molec·s^-1·Å^-2). Example: `KMCOutput.tof['CO2']`

### Coverage
- **coverage** (*dict*): Coverage of surface species (in %). Example: `KMCOutput.coverage['CO']`
- **av_coverage** (*dict*): Average coverage of surface species (in %). Example: `KMCOutput.av_coverage['CO']`
- **total_coverage** (*np.Array*): Total coverage of surface species (in %).
- **av_total_coverage** (*float*): Average total coverage of surface species (in %).
- **dominant_ads** (*str*): Most dominant surface species, used to plot the kinetic phase diagrams.
- **coverage_per_site_type** (*dict*): Coverage of surface species per site type (in %).
- **av_coverage_per_site_type** (*dict*): Average coverage of surface species per site type (in %).
- **total_coverage_per_site_type** (*dict*): Total coverage of surface species per site type (in %). Example: 
`KMCOutput.total_coverage_per_site_type['top']`
- **av_total_coverage_per_site_type** (*dict*): Average total coverage of surface species per site type (in %).
- **dominant_ads_per_site_type** (*dict*): Most dominant surface species per site type, used to plot the kinetic phase 
diagrams.

### Selectivity
The selectivity can be obtained by using the `get_selectivity()` method 
{py:meth}`zacrostools.kmc_output.KMCOutput.get_selectivity()`, which requires to parameters:

- **main_product** (*str*): Name of the main product
- **side_products** (*list*): Names of the side products

Example:

    selectivity = kmc_output.get_selectivity(main_product='CH4', side_products=['CO2', 'CH3OH'])  # in %

### 3. Print simulation data (examples)

#### TOF

    for gas_species in kmc_output.gas_species_names
        tof = kmc_output.tof[gas_species]
        print(f"TOF {gas_species}: {tof:.3e} molec·s^-1·Å^-2")

#### Selectivity

    for gas_species in kmc_output.gas_species_names
        tof = kmc_output.tof[gas_species]
        print(f"TOF {gas_species}: {tof:.3e} molec·s^-1·Å^-2")

#### Coverage per total number of sites

    for surf_species in kmc_output.surf_species_names:
        coverage = kmc_output.coverage[surf_species]
        print(f"Coverage {surf_species}: {coverage:.3f} % of total sites")

#### Coverage per total number of sites of a given type

    for site_type in kmc_output.site_types:
        for surf_species in kmc_output.coverage_per_site_type[site_type]:
            coverage = kmc_output.coverage_per_site_type[site_type][surf_species]
            print(f"Coverage {surf_species}: {coverage:.3f} % of {site_type} sites")


```{warning}
This section of the documentation is under development. 
```