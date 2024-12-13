# Reading output files

## 1. Store simulation data in a `KMCOutput` object

All the information about a finished *Zacros* simulation can be extracted by creating a `KMCOutput` object using `zacrostools.kmc_output.KMCOutput`.

### Example

```python
from zacrostools.kmc_output import KMCOutput

kmc_output = KMCOutput(path='.', analysis_range=[50, 100], range_type='time', weights='time')
```

### Arguments

**Mandatory:**

- **`path`** (*str*): Path of the directory containing the output files.

**Optional:**

- **`analysis_range`** (*list*): A list of two elements `[initial_percent, final_percent]` specifying the window of the total simulation. The values should be between 0 and 100, representing the percentage of the total simulated time or the total number of events to be considered.
  - Default: `[0.0, 100.0]`

- **`range_type`** (*str*): The type of window to apply when calculating averages (e.g., `av_coverage`) or TOF. Possible values:
  - `'time'`: Apply a window over the simulated time.
  - `'nevents'`: Apply a window over the number of simulated events.
  - Default: `'time'`

- **`weights`** (*str*): Weights for calculating the weighted average. Possible values:
  - `'time'`
  - `'nevents'`
  - `None` (all weights are set to 1)
  - Default: `None`

## 2. Read simulation data from a `KMCOutput` object

All KMC results can be obtained from the different `KMCOutput` attributes.

### General simulation data

- **`random_seed`** (*int*): Random seed used in the simulation.
- **`temperature`** (*float*): Temperature used in the simulation (in Kelvin).
- **`pressure`** (*float*): Total pressure used in the simulation (in bar).
- **`n_gas_species`** (*int*): Number of gas species.
- **`gas_specs_names`** (*list of str*): Gas species names.
- **`gas_molar_fracs`** (*list of float*): Molar fractions of gas species.
- **`n_surf_species`** (*int*): Number of surface species.
- **`surf_specs_names`** (*list of str*): Surface species names.
- **`n_sites`** (*int*): Total number of lattice sites.
- **`area`** (*float*): Lattice surface area (in Å²).
- **`site_types`** (*dict*): Site type names and the total number of sites of each type.

### Events

- **`nevents`** (*np.ndarray*): Number of KMC events occurred.

### Simulated time

- **`time`** (*np.ndarray*): Simulated time (in seconds).
- **`final_time`** (*float*): Final simulated time (in seconds).

### Lattice energy

- **`energy`** (*np.ndarray*): Lattice energy (in eV·Å⁻²).
- **`av_energy`** (*float*): Average lattice energy (in eV·Å⁻²).
- **`final_energy`** (*float*): Final lattice energy (in eV·Å⁻²).
- **`energy_slope`** (*float*): Slope of the lattice energy over the number of events (in eV·Å⁻²·step⁻¹). A high value may indicate that the simulation has not reached steady-state.

### Molecules consumed/produced and TOF

- **`production`** (*dict*): Gas species produced over time (in molecules). Example: `kmc_output.production['CO']`.
- **`total_production`** (*dict*): Total number of gas species produced (in molecules). Example: `kmc_output.total_production['CO']`.
- **`tof`** (*dict*): TOF of gas species (in molecules·s⁻¹·Å⁻²). Example: `kmc_output.tof['CO2']`.

### Coverage

- **`coverage`** (*dict*): Coverage of surface species over time (in %). Example: `kmc_output.coverage['CO']`.
- **`av_coverage`** (*dict*): Average coverage of surface species (in %). Example: `kmc_output.av_coverage['CO']`.
- **`total_coverage`** (*np.ndarray*): Total coverage of surface species over time (in %).
- **`av_total_coverage`** (*float*): Average total coverage of surface species (in %).
- **`dominant_ads`** (*str*): Most dominant surface species, used to plot kinetic phase diagrams.

### Coverage per site type

- **`coverage_per_site_type`** (*dict*): Coverage of surface species per site type over time (in %). Example: `kmc_output.coverage_per_site_type['top']['CO']`.
- **`av_coverage_per_site_type`** (*dict*): Average coverage of surface species per site type (in %). Example: `kmc_output.av_coverage_per_site_type['top']['CO']`.
- **`total_coverage_per_site_type`** (*dict*): Total coverage of surface species per site type over time (in %). Example: `kmc_output.total_coverage_per_site_type['top']`.
- **`av_total_coverage_per_site_type`** (*dict*): Average total coverage of surface species per site type (in %). Example: `kmc_output.av_total_coverage_per_site_type['top']`.
- **`dominant_ads_per_site_type`** (*dict*): Most dominant surface species per site type, used to plot kinetic phase diagrams. Example: `kmc_output.dominant_ads_per_site_type['top']`.

## 3. Methods

### `get_selectivity()`

Calculate the selectivity of the main product over side products.

**Parameters:**

- **`main_product`** (*str*): Name of the main product.
- **`side_products`** (*list of str*): Names of the side products.

**Returns:**

- (*float*): The selectivity of the main product (in %) over the side products.

**Notes:**

The selectivity is calculated as:

```python
selectivity = (TOF_main_product / (TOF_main_product + sum(TOF_side_products))) * 100
```

If the total TOF is zero, the selectivity is returned as `NaN`.

**Example:**

```python
selectivity = kmc_output.get_selectivity(main_product='CH4', side_products=['CO2', 'CH3OH'])  # in %
```

## 4. Print simulation data (examples)

### TOF

```python
for gas_species in kmc_output.gas_specs_names:
    tof = kmc_output.tof[gas_species]
    print(f"TOF {gas_species}: {tof:.3e} molecules·s⁻¹·Å⁻²")
```

### Selectivity

```python
selectivity = kmc_output.get_selectivity(main_product='CH4', side_products=['CO2', 'CH3OH'])
print(f"Selectivity for CH4: {selectivity:.2f} %")
```

### Average coverage per total number of sites

```python
for surf_species in kmc_output.surf_specs_names:
    coverage = kmc_output.av_coverage[surf_species]
    print(f"Average coverage of {surf_species}: {coverage:.3f} % of total sites")
```

### Average coverage per site type

```python
for site_type in kmc_output.site_types:
    for surf_species in kmc_output.coverage_per_site_type[site_type]:
        coverage = kmc_output.av_coverage_per_site_type[site_type][surf_species]
        print(f"Average coverage of {surf_species} on {site_type} sites: {coverage:.3f} %")
```

### Energy slope

```python
print(f"Energy slope: {kmc_output.energy_slope:.3e} eV·Å⁻²·step⁻¹")
```
