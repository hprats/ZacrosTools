# Reading Output Files

## 1. Store Simulation Data in a `KMCOutput` Object

All the information about a finished Zacros simulation can be extracted by creating a `KMCOutput` object using {py:func}`zacrostools.kmc_output.KMCOutput`.

### Example

```python
from zacrostools.kmc_output import KMCOutput

kmc_output = KMCOutput(path='zacros_results', ignore=30.0)
```

### Arguments

**Mandatory:**
- **path** (*str*): Path of the directory containing the output files.

**Optional:**
- **ignore** (*float*): Ignore the first % of the total simulated time (in %). This is used to exclude the data from the equilibration phase when computing the averages.
  - Default value: `0.0`.
- **weights** (*str*): Weights for the averages. Possible values:
  - `'time'`
  - `'events'`
  - `None`, all weights are set to 1.
  - Default value: `None`.

## 2. Read Simulation Data from a `KMCOutput` Object

All KMC results can be obtained from the different `KMCOutput` attributes.

### General Simulation Data
- **n_gas_species** (*int*): Number of gas species.
- **gas_species_names** (*list of str*): Gas species names.
- **n_surf_species** (*int*): Number of surface species.
- **surf_species_names** (*list of str*): Surface species names.
- **n_sites** (*int*): Total number of lattice sites.
- **area** (*float*): Lattice surface area (in Å²).
- **site_types** (*dict*): Site type names and the total number of sites of each type.

### Simulated Time
- **time** (*np.Array*): Simulated time (in seconds).
- **final_time** (*float*): Final simulated time (in seconds).

### Lattice Energy
- **energy** (*np.Array*): Lattice energy (in eV·Å⁻²).
- **av_energy** (*float*): Average lattice energy (in eV·Å⁻²).
- **final_energy** (*float*): Final lattice energy (in eV·Å⁻²).

### Molecules Consumed/Produced and TOF
- **production** (*dict*): Gas species produced. 
  - Example: `KMCOutput.production['CO']`.
- **total_production** (*dict*): Total number of gas species produced. 
  - Example: `KMCOutput.total_production['CO']`.
- **tof** (*dict*): TOF of gas species (in molec·s⁻¹·Å⁻²). 
  - Example: `KMCOutput.tof['CO2']`.

### Coverage
- **coverage** (*dict*): Coverage of surface species (in %). 
  - Example: `KMCOutput.coverage['CO']`.
- **av_coverage** (*dict*): Average coverage of surface species (in %). 
  - Example: `KMCOutput.av_coverage['CO']`.
- **total_coverage** (*np.Array*): Total coverage of surface species (in %).
  - Example: `KMCOutput.total_coverage`.
- **av_total_coverage** (*float*): Average total coverage of surface species (in %).
  - Example: `KMCOutput.av_total_coverage`.
- **dominant_ads** (*str*): Most dominant surface species, used to plot the kinetic phase diagrams.
  - Example: `KMCOutput.dominant_ads`.
- **coverage_per_site_type** (*dict*): Coverage of surface species per site type (in %).
  - Example: `KMCOutput.coverage_per_site_type['top']['CO']`.
- **av_coverage_per_site_type** (*dict*): Average coverage of surface species per site type (in %).
  - Example: `KMCOutput.av_coverage_per_site_type['top']['CO']`.
- **total_coverage_per_site_type** (*dict*): Total coverage of surface species per site type (in %). 
  - Example: `KMCOutput.total_coverage_per_site_type['top']`.
- **av_total_coverage_per_site_type** (*dict*): Average total coverage of surface species per site type (in %).
  - Example: `KMCOutput.av_total_coverage_per_site_type['top']`.
- **dominant_ads_per_site_type** (*dict*): Most dominant surface species per site type, used to plot the kinetic phase 
diagrams.
  - Example: `KMCOutput.dominant_ads_per_site_type['top']`.

### Selectivity
The selectivity can be obtained by using the `get_selectivity()` method {py:meth}`zacrostools.kmc_output.KMCOutput.get_selectivity()`, which requires two parameters:

- **main_product** (*str*): Name of the main product.
- **side_products** (*list*): Names of the side products.

### Example

```python
selectivity = kmc_output.get_selectivity(main_product='CH4', side_products=['CO2', 'CH3OH'])  # in %
```

## 3. Print Simulation Data (Examples)

### TOF

```python
for gas_species in kmc_output.gas_species_names:
    tof = kmc_output.tof[gas_species]
    print(f"TOF {gas_species}: {tof:.3e} molec·s⁻¹·Å⁻²")
```

### Selectivity

```python
for gas_species in kmc_output.gas_species_names:
    selectivity = kmc_output.get_selectivity(main_product=gas_species, side_products=['CO2', 'CH3OH'])
    print(f"Selectivity for {gas_species}: {selectivity:.2f} %")
```

### Coverage per Total Number of Sites

```python
for surf_species in kmc_output.surf_species_names:
    coverage = kmc_output.coverage[surf_species]
    print(f"Coverage {surf_species}: {coverage:.3f} % of total sites")
```

### Coverage per Total Number of Sites of a Given Type

```python
for site_type in kmc_output.site_types:
    for surf_species in kmc_output.coverage_per_site_type[site_type]:
        coverage = kmc_output.coverage_per_site_type[site_type][surf_species]
        print(f"Coverage {surf_species}: {coverage:.3f} % of {site_type} sites")
```

```{warning}
This section of the documentation is under development.
```
