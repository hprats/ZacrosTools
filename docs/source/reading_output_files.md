# Reading output files

## Overview

After completing a Zacros simulation, you can use `zacrostools` to parse and analyze the results. The `KMCOutput` class provides a convenient interface to load simulation data from output files, compute averages and coverages, and extract key performance indicators like turnover frequencies (TOFs) and selectivities. This unified approach simplifies the post-processing workflow, making it straightforward to analyze multiple simulations or perform parametric studies.

---

## Creating a `KMCOutput` object

To extract simulation results, instantiate a `KMCOutput` object by pointing it to the directory containing the Zacros output files. You can also specify analysis ranges and weighting schemes for averaging results, giving you fine-grained control over the portion of the simulation data you want to analyze.

### Example

```python
from zacrostools.kmc_output import KMCOutput

# Create a KMCOutput object to read data from the current directory.
# Here, we consider the last 50% of the simulation time and apply time-weighted averaging.
kmc_output = KMCOutput(path='.', analysis_range=[50, 100], range_type='time', weights='time')
```

### Arguments

**Mandatory:**

- **`path`** (*str*): Path to the directory containing the Zacros output files (e.g., `simulation_input.dat`, `general_output.txt`, `specnum_output.txt`, etc.).

**Optional:**

- **`analysis_range`** (*list*, default: `[0.0, 100.0]`): Defines the segment of the simulation considered for averaging and analysis. The two-element list `[start_percent, end_percent]` specifies the portion of the simulation to use. For instance, `[50, 100]` focuses on the last half of the simulation.
  
- **`range_type`** (*str*, default: `'time'`): Determines how `analysis_range` is interpreted:
  - `'time'`: The percentages refer to segments of total simulated time.
  - `'nevents'`: The percentages refer to segments of the total number of simulated events.
  
- **`weights`** (*str*, default: `None`): Sets the weighting scheme for averaging:
  - `'time'`: Weighted by the time interval between data points.
  - `'nevents'`: Weighted by the number of events between data points.
  - `None`: No weighting (all data points are equally weighted).

---

## Accessing simulation data

Once you have created a `KMCOutput` object, you can access a variety of data fields. These data fields include simulation conditions, reaction outcomes, coverage profiles, and calculated averages. The attributes and their meanings are summarized below.

### General simulation data

- **`random_seed`** (*int*): Random seed used by Zacros.
- **`temperature`** (*float*): Simulation temperature (K).
- **`pressure`** (*float*): Total pressure (bar).
- **`n_gas_species`** (*int*): Number of gas-phase species.
- **`gas_specs_names`** (*list of str*): Names of the gas-phase species.
- **`gas_molar_fracs`** (*list of float*): Molar fractions of each gas species.
- **`n_surf_species`** (*int*): Number of surface-bound species.
- **`surf_specs_names`** (*list of str*): Names of the surface species.
- **`n_sites`** (*int*): Total number of lattice sites.
- **`area`** (*float*): Catalyst surface area (Å²).
- **`site_types`** (*dict*): Mapping of site types to the number of sites of each type (e.g., `{'top': 50, 'bridge': 50}`).

### Events and time

- **`nevents`** (*np.ndarray*): Array of integers representing the cumulative number of KMC events at each recorded data point.
- **`time`** (*np.ndarray*): Simulated time at each data point (s).
- **`finaltime`** (*float*): Final simulation time (s).

### Lattice energy

- **`energy`** (*np.ndarray*): Lattice energy over time (eV·Å⁻²).
- **`av_energy`** (*float*): Time/Events-weighted average lattice energy (eV·Å⁻²).
- **`final_energy`** (*float*): Final lattice energy (eV·Å⁻²).
- **`energyslope`** (*float*): Slope of energy vs. events (eV·Å⁻²·step⁻¹). A large slope may suggest the simulation did not reach steady-state.

### Gas production and TOF

- **`production`** (*dict*): Dictionary of arrays tracking the cumulative production of each gas species over time (in molecules). For example, `kmc_output.production['CO']` gives an array of CO production values.
- **`total_production`** (*dict*): Total number of molecules produced for each gas species by the end of the simulation. Example: `kmc_output.total_production['CO']`.
- **`tof`** (*dict*): Turnover frequency of each gas species (molecules·s⁻¹·Å⁻²), indicating production rate normalized by the catalyst area. For example, `kmc_output.tof['CO2']`.

### Surface coverage

- **`coverage`** (*dict*): Coverage of each surface species over time, expressed as a percentage of total sites. Example: `kmc_output.coverage['CO']` gives an array of CO coverage values.
- **`av_coverage`** (*dict*): Weighted average coverage of each surface species over the analysis window. Example: `kmc_output.av_coverage['CO']`.
- **`total_coverage`** (*np.ndarray*): Total coverage of all surface species combined, over time (%).
- **`av_total_coverage`** (*float*): Average total coverage (%).
- **`dominant_ads`** (*str*): The surface species with the highest average coverage.

### Coverage per site type

To gain more detailed insight, you can also access coverage data broken down by site type:

- **`coverage_per_site_type`** (*dict*): Nested dictionaries of coverage by site type and species over time. Example: `kmc_output.coverage_per_site_type['top']['CO']`.
- **`av_coverage_per_site_type`** (*dict*): Weighted average coverage per site type and species. Example: `kmc_output.av_coverage_per_site_type['top']['CO']`.
- **`total_coverage_per_site_type`** (*dict*): Total coverage per site type over time (%).
- **`av_total_coverage_per_site_type`** (*dict*): Average total coverage per site type (%).
- **`dominant_ads_per_site_type`** (*dict*): Dominant adsorbed species on each site type.

---

## Methods

### `get_selectivity()`

The `get_selectivity()` method calculates the selectivity of a main product relative to other side products, providing a measure of reaction specificity.

**Parameters:**

- **`main_product`** (*str*): Main product species name.
- **`side_products`** (*list of str*): List of side product species names.

**Returns:**

- (*float*): Selectivity (in %) of the main product over the side products.

**Notes:**

The selectivity is defined as:

```python
selectivity = (TOF_main_product / (TOF_main_product + sum(TOF_side_products))) * 100
```

If the denominator is zero (no products formed), the method returns `NaN`.

**Example:**

```python
selectivity = kmc_output.get_selectivity(main_product='CH4', side_products=['CO2', 'CH3OH'])
print(f"CH4 Selectivity: {selectivity:.2f} %")
```

---

## Examples of usage

### Printing TOFs

```python
for gas_species in kmc_output.gas_specs_names:
    tof = kmc_output.tof[gas_species]
    print(f"TOF of {gas_species}: {tof:.3e} molecules·s⁻¹·Å⁻²")
```

### Checking selectivity

```python
selectivity = kmc_output.get_selectivity(main_product='CH4', side_products=['CO2', 'CH3OH'])
print(f"Selectivity for CH4: {selectivity:.2f} %")
```

### Average coverage on total sites

```python
for surf_species in kmc_output.surf_specs_names:
    avg_cov = kmc_output.av_coverage[surf_species]
    print(f"Average coverage of {surf_species}: {avg_cov:.3f} % of total sites")
```

### Average coverage per site type

```python
for stype in kmc_output.site_types:
    for sps in kmc_output.av_coverage_per_site_type[stype]:
        avg_cov = kmc_output.av_coverage_per_site_type[stype][sps]
        print(f"Average coverage of {sps} on {stype} sites: {avg_cov:.3f} %")
```

### Energy slope

```python
print(f"Energy slope: {kmc_output.energyslope:.3e} eV·Å⁻²·step⁻¹")
```