# Reading output files

After completing a Zacros simulation, `zacrostools` can be used to parse and analyze the results. 

---

#### Extract data from a single simulation

The `KMCOutput` class provides a convenient interface to load simulation data from output files, compute averages and coverages, and extract key performance indicators like turnover frequencies (TOFs) and selectivities.

Required parameters: 
- **`path`** (`str`): Path to the directory containing Zacros output files (e.g., `simulation_input.dat`, `general_output.txt`, `specnum_output.txt`, etc.).  
- **`analysis_range`** (`list`, *optional*): Portion of the simulation used for averaging and analysis (`[start%, end%]`, default = `[0.0, 100.0]`).  
  Example: `[50, 100]` analyzes only the last half of the simulation.  
- **`range_type`** (`str`, *optional*): Defines how `analysis_range` is interpreted (default = `'time'`).  
  - `'time'`: Percentages refer to total simulated time.  
  - `'nevents'`: Percentages refer to total number of simulated events.  
- **`weights`** (`str`, *optional*): Weighting scheme for averaging (default = `None`).  
  - `'time'`: Weighted by time intervals.  
  - `'nevents'`: Weighted by number of events.  
  - `None`: Equal weights for all data points.  

```python
from zacrostools.kmc_output import KMCOutput

# Here, we consider the last 50% of the simulation time and apply time-weighted averaging.
kmc_output = KMCOutput(path='/path/to/simulation_files', analysis_range=[50, 100], range_type='time', weights='time')
```

Once you have created a `KMCOutput` object, you can access all the information using the following attributes:

General simulation data:
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

Events and time:
- **`nevents`** (*np.ndarray*): Array of integers representing the cumulative number of KMC events at each recorded data point.
- **`time`** (*np.ndarray*): Simulated time at each data point (s).
- **`finaltime`** (*float*): Final simulation time (s).

Lattice energy:
- **`energy`** (*np.ndarray*): Lattice energy over time (eV·Å⁻²).
- **`av_energy`** (*float*): Time/Events-weighted average lattice energy (eV·Å⁻²).
- **`final_energy`** (*float*): Final lattice energy (eV·Å⁻²).
- **`energyslope`** (*float*): Slope of energy vs. events (eV·Å⁻²·step⁻¹). A large slope may suggest the simulation did not reach steady-state.

Gas production and TOF:
- **`production`** (*dict*): Dictionary of arrays tracking the cumulative production of each gas species over time (in molecules). For example, `kmc_output.production['CO']` gives an array of CO production values.
- **`total_production`** (*dict*): Total number of molecules produced for each gas species by the end of the simulation. Example: `kmc_output.total_production['CO']`.
- **`tof`** (*dict*): Turnover frequency of each gas species (molecules·s⁻¹·Å⁻²), indicating production rate normalized by the catalyst area. For example, `kmc_output.tof['CO2']`.

Surface coverage:
- **`coverage`** (*dict*): Coverage of each surface species over time, expressed as a percentage of total sites. Example: `kmc_output.coverage['CO']` gives an array of CO coverage values.
- **`av_coverage`** (*dict*): Weighted average coverage of each surface species over the analysis window. Example: `kmc_output.av_coverage['CO']`.
- **`total_coverage`** (*np.ndarray*): Total coverage of all surface species combined, over time (%).
- **`av_total_coverage`** (*float*): Average total coverage (%).
- **`dominant_ads`** (*str*): The surface species with the highest average coverage.
- **`coverage_per_site_type`** (*dict*): Nested dictionaries of coverage by site type and species over time. Example: `kmc_output.coverage_per_site_type['top']['CO']`.
- **`av_coverage_per_site_type`** (*dict*): Weighted average coverage per site type and species. Example: `kmc_output.av_coverage_per_site_type['top']['CO']`.
- **`total_coverage_per_site_type`** (*dict*): Total coverage per site type over time (%).
- **`av_total_coverage_per_site_type`** (*dict*): Average total coverage per site type (%).
- **`dominant_ads_per_site_type`** (*dict*): Dominant adsorbed species on each site type.

Finally, the selectivity can be obtained using the `get_selectivity()` method. The following parameters are required:
- **`main_product`** (*str*): Main product species name.
- **`side_products`** (*list of str*): List of side product species names.

Note that the selectivity is defined as:

```python
selectivity = (TOF_main_product / (TOF_main_product + sum(TOF_side_products))) * 100
```

```python
from zacrostools.kmc_output import KMCOutput

# Read simulation output
kmc_output = KMCOutput(
    path='temp_600K',
    analysis_range=[50, 100],
    range_type='time',
    weights='time')

# Print TOF of all gas-phase species
for gas_spec in kmc_output.gas_specs_names:
    tof = kmc_output.tof[gas_spec]
    print(f"{gas_spec}: {tof:.3e} molec·s⁻¹·Å⁻²")

# Compute selectivity of CH4 vs CO2 and CH3OH
select_ch4 = kmc_output.get_selectivity(
    main_product='CH4',
    side_products=['CO2', 'CH3OH'])
print(f"Selectivity of CH4: {select_ch4:.2f}%")

# Print average coverage of all surface species
for surf_spec in kmc_output.surf_specs_names:
    avg_cov = kmc_output.av_coverage[surf_spec]
    print(f"{surf_spec}: {avg_cov:.2f}%")
```

#### Extract data from multiple simulations

The `read_scan` function can be used to read the results of all KMC simulations in a given scan directory. This function returns a Pandas DataFrame containing key observables for each simulation.

#### Example

```python
from zacrostools.read_scan import read_scan

data_scan = read_scan(
    scan_path='path_to_scan',
    analysis_range=[50, 100],
    range_type='time')
data_scan.to_csv('data_scan.csv', index=True)
```
