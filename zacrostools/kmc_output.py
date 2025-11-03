import os
import numpy as np
from typing import Union
from zacrostools.simulation_input import parse_simulation_input_file
from zacrostools.general_output import parse_general_output_file
from zacrostools.specnum_output import parse_specnum_output_file
from zacrostools.custom_exceptions import enforce_types, KMCOutputError, EnergeticsModelError


class KMCOutput:

    """
    A class that represents a KMC (Kinetic Monte Carlo) simulation output.

    Attributes
    ----------
    area : float
        Lattice surface area (in Å²).
    av_coverage : Dict[str, float]
        Average coverage of surface species (in %). Example: `KMCOutput.av_coverage['CO']`.
    av_coverage_per_site_type : Dict[str, Dict[str, float]]
        Average coverage of surface species per site type (in %).
    av_energy : float
        Average lattice energy (in eV·Å⁻²).
    av_total_coverage : float
        Average total coverage of surface species (in %).
    av_total_coverage_per_site_type : Dict[str, float]
        Average total coverage of surface species per site type (in %).
    coverage : Dict[str, np.ndarray]
        Coverage of surface species over time (in %). Example: `KMCOutput.coverage['CO']`.
    coverage_per_site_type : Dict[str, Dict[str, np.ndarray]]
        Coverage of surface species per site type over time (in %).
    cpu_time : float
        Final elapsed cpu time (in seconds).
    dominant_ads : str
        Most dominant surface species, used for plotting kinetic phase diagrams.
    dominant_ads_per_site_type : Dict[str, str]
        Most dominant surface species per site type, used for plotting kinetic phase diagrams.
    energy : np.ndarray
        Lattice energy (in eV·Å⁻²).
    final_energy : float
        Final lattice energy (in eV·Å⁻²).
    finaltime : float
        Final simulated time (in seconds).
    gas_specs_names : List[str]
        Gas species names.
    n_gas_species : int
        Number of gas species.
    n_sites : int
        Total number of lattice sites.
    n_surf_species : int
        Number of surface species.
    nevents : np.ndarray
        Number of events occurred.
    production : Dict[str, np.ndarray]
        Gas species produced over time. Example: `KMCOutput.production['CO']`.
    surf_specs_names : List[str]
        Surface species names.
    time : np.ndarray
        Simulated time (in seconds).
    tof : Dict[str, float]
        TOF (Turnover Frequency) of gas species (in molecules·s⁻¹·Å⁻²). Example: `KMCOutput.tof['CO2']`.
    total_coverage : np.ndarray
        Total coverage of surface species over time (in %).
    total_coverage_per_site_type : Dict[str, np.ndarray]
        Total coverage of surface species per site type over time (in %). Example: `KMCOutput.total_coverage_per_site_type['top']`.
    total_production : Dict[str, float]
        Total number of gas species produced. Example: `KMCOutput.total_production['CO']`.
    """

    def __init__(self, job_path: str = None, analysis_range: Union[list, None] = None, range_type: str = 'time',
                 weights: Union[str, None] = None, **kwargs):
        """
        Initialize the KMCOutput object by parsing simulation output files.

        Parameters
        ----------
        job_path : str, optional
            The path where the output files are located. (Previously named 'path'.)
            For backward compatibility, you can still pass this value using the keyword 'path'.
        analysis_range : List[float], optional
            A list of two elements `[start_percent, end_percent]` specifying the portion of the entire simulation
            to consider for analysis. The values should be between 0 and 100, representing percentages of the
            total simulated time or the total number of events, depending on `range_type`. For example,
            `[50, 100]` would analyze only the latter half of the simulation. Default is `[0.0, 100.0]`.
        range_type : str, optional
            Determines the dimension used when applying `analysis_range`:
            - `'time'`: The percentages in `analysis_range` refer to segments of the total simulated time.
            - `'nevents'`: The percentages in `analysis_range` refer to segments of the total number of simulated events.
            Default is `'time'`.
        weights : str, optional
            Weights for calculating weighted averages. Possible values are `'time'`, `'nevents'`, or `None`.
            If `None`, all weights are set to 1. Default value is `None`.
        """
        # Support backward compatibility: if job_path is not provided, check for 'path'
        if job_path is None:
            job_path = kwargs.pop('path', None)
        if job_path is None:
            raise TypeError("Missing required argument: job_path (or 'path' for backwards compatibility)")
        self.job_path = job_path

        if analysis_range is None:
            analysis_range = [0.0, 100.0]

        # Parse relevant data from the simulation_input.dat file
        data_simulation = parse_simulation_input_file(
            input_file=f'{self.job_path}/simulation_input.dat')

        self.random_seed = data_simulation['random_seed']
        self.temperature = data_simulation['temperature']
        self.pressure = data_simulation['pressure']
        self.n_gas_species = data_simulation['n_gas_species']
        self.gas_specs_names = data_simulation['gas_specs_names']
        self.gas_molar_fracs = data_simulation['gas_molar_fracs']
        self.n_surf_species = data_simulation['n_surf_species']
        self.surf_specs_names = data_simulation['surf_specs_names']
        self.surf_specs_dent = data_simulation['surf_specs_dent']

        # Parse relevant data from the general_output.txt file
        data_general = parse_general_output_file(
            output_file=f'{self.job_path}/general_output.txt')

        self.n_sites = data_general['n_sites']
        self.area = data_general['area']
        self.site_types = data_general['site_types']
        self.cpu_time = data_general['cpu_time']

        # Parse relevant data from the specnum_output.txt file
        data_specnum, header = parse_specnum_output_file(
            output_file=f'{self.job_path}/specnum_output.txt',
            analysis_range=analysis_range,
            range_type=range_type)

        self.nevents = data_specnum[:, 1]
        self.time = data_specnum[:, 2]
        self.final_time = data_specnum[-1, 2]
        self.energy = data_specnum[:, 4] / self.area  # in eV/Å2

        # If the energy is constant, avoid numerical noise in polyfit by setting slope to zero.
        if np.ptp(self.energy) > 1e-12:
            self.energyslope = abs(np.polyfit(self.nevents, self.energy, 1)[0])  # in eV/Å²/step
        else:
            self.energyslope = 0.0

        self.final_energy = data_specnum[-1, 4] / self.area
        self.av_energy = self.get_average(array=self.energy, weights=weights)

        # Compute production and TOF
        self.production = {}  # in molecules
        self.total_production = {}  # useful when calculating selectivity (i.e., set min_total_production)
        self.tof = {}  # in molecules·s⁻¹·Å⁻²
        for i in range(5 + self.n_surf_species, len(header)):
            gas_spec = header[i]
            self.production[gas_spec] = data_specnum[:, i]
            self.total_production[gas_spec] = data_specnum[-1, i] - data_specnum[0, i]

            gas_data = data_specnum[:, i]
            # Check if production is constant using the peak-to-peak difference.
            if len(gas_data) > 1 and np.ptp(gas_data) > 1e-18:
                slope = np.polyfit(data_specnum[:, 2], gas_data, 1)[0]
                # Force slope to zero if it is within a small tolerance.
                if np.isclose(slope, 0, atol=1e-18):
                    slope = 0.0
                self.tof[gas_spec] = slope / self.area
            else:
                self.tof[gas_spec] = 0.0

        # Compute coverages (per total number of sites)
        dent_sites_map = get_dentate_types(job_path=self.job_path)
        self.coverage = {}
        self.av_coverage = {}
        for i in range(5, 5 + self.n_surf_species):
            surf_spec = header[i]
            dent_sites = dent_sites_map[surf_spec]
            total_dentates = len(dent_sites)
            # total occupied sites = #molecules * #dentates per molecule
            self.coverage[surf_spec] = data_specnum[:, i] * total_dentates / self.n_sites * 100
            self.av_coverage[surf_spec] = self.get_average(
                array=self.coverage[surf_spec], weights=weights
            )
        self.total_coverage = sum(self.coverage.values())
        self.av_total_coverage = min(sum(self.av_coverage.values()), 100)
        self.dominant_ads = max(self.av_coverage, key=self.av_coverage.get)

        # Compute partial coverages (per total number of sites of each site_type)
        self.coverage_per_site_type = {st: {} for st in self.site_types}
        self.av_coverage_per_site_type = {st: {} for st in self.site_types}
        for i in range(5, 5 + self.n_surf_species):
            surf_spec = header[i]
            dent_sites = dent_sites_map[surf_spec]
            for site_type, n_sites_type in self.site_types.items():
                # number of dentates of this species on this site_type
                n_dents_on_type = dent_sites.count(site_type)
                self.coverage_per_site_type[site_type][surf_spec] = (
                    data_specnum[:, i] * n_dents_on_type / n_sites_type * 100
                )
                self.av_coverage_per_site_type[site_type][surf_spec] = self.get_average(
                    array=self.coverage_per_site_type[site_type][surf_spec],
                    weights=weights
                )

        self.total_coverage_per_site_type = {}
        self.av_total_coverage_per_site_type = {}
        self.dominant_ads_per_site_type = {}
        for site_type, cov_dict in self.av_coverage_per_site_type.items():
            if cov_dict:
                self.total_coverage_per_site_type[site_type] = sum(
                    self.coverage_per_site_type[site_type].values()
                )
                self.av_total_coverage_per_site_type[site_type] = min(
                    sum(cov_dict.values()), 100
                )
                self.dominant_ads_per_site_type[site_type] = max(
                    cov_dict, key=cov_dict.get
                )
            else:
                # no adsorption on this site_type
                self.total_coverage_per_site_type[site_type] = np.zeros_like(self.time)
                self.av_total_coverage_per_site_type[site_type] = 0.0
                self.dominant_ads_per_site_type[site_type] = None


    def get_average(self, array, weights):
        """
        Calculate the average of an array with optional weighting.

        Parameters
        ----------
        array : np.ndarray
            The array of values to average.
        weights : str or None
            The weights to apply when calculating the average. Possible values are:
            - `None`: No weighting; all weights are set to 1.
            - `'time'`: Weights based on the differences in simulated time.
            - `'nevents'`: Weights based on the differences in the number of events.

        Returns
        -------
        float
            The calculated average value.
        """
        if weights not in [None, 'time', 'nevents']:
            raise KMCOutputError(f"'weights' must be one of the following: 'none' (default), 'time', or 'nevents'.")

        if len(array) == 1:
            # If the catalyst is poisoned, it could be that the last ∆t is very high and the time window only
            # contains one row. In that case, do not compute the average
            return float(array[0])
        else:
            if weights is None:
                return np.average(array)
            elif weights == 'time':
                return np.average(array[1:], weights=np.diff(self.time))
            elif weights == 'nevents':
                return np.average(array[1:], weights=np.diff(self.nevents))

    @enforce_types
    def get_selectivity(self, main_product: str, side_products: list):
        """
        Calculate the selectivity of the main product over side products.

        Parameters
        ----------
        main_product : str
            Name of the main product.
        side_products : List[str]
            Names of the side products.

        Returns
        -------
        float
            The selectivity of the main product (in %) over the side products.

        Notes
        -----
        The selectivity is calculated as:
            selectivity = (TOF_main_product / (TOF_main_product + sum(TOF_side_products))) * 100

        If the total TOF is zero, the selectivity is returned as NaN.
        """
        selectivity = float('NaN')
        tof_side_products = 0.0
        for side_product in side_products:
            tof_side_products += self.tof[side_product]
        if self.tof[main_product] + tof_side_products != 0:
            selectivity = self.tof[main_product] / (self.tof[main_product] + tof_side_products) * 100
        return selectivity


def get_dentate_types(job_path: str = None, **kwargs):
    """
    Retrieve surface species data including the number of dentates and the associated site types for each surface species.

    Parameters
    ----------
    job_path : str, optional
        The path to the directory containing the simulation input files (simulation_input.dat and energetics_input.dat).
        (Previously named 'path'.) For backward compatibility, you can pass 'path' instead.

    Returns
    -------
    dict
        A dictionary mapping each surface species name to a list of site types indexed by dentate number (1-based).
    """
    import warnings
    # backward compatibility for 'path'
    if job_path is None:
        job_path = kwargs.pop('path', None)
    if job_path is None:
        raise TypeError("Missing required argument: job_path (or 'path' for backwards compatibility)")

    # parse simulation input for species and dentates
    sim_data = parse_simulation_input_file(input_file=f"{job_path}/simulation_input.dat")
    surf_specs = sim_data.get('surf_specs_names', [])
    dent_counts = sim_data.get('surf_specs_dent', [])
    species_dentates = dict(zip(surf_specs, dent_counts))

    # default lattice: every dentate on default site
    if check_default_lattice(job_path=job_path):
        return {spec: ['StTp1'] * species_dentates[spec] for spec in surf_specs}

    # container for global species->dentate mapping
    species_mapping = {}  # species -> {dentate_index: site_type}

    # read energetics_input.dat
    with open(os.path.join(job_path, 'energetics_input.dat'), 'r') as f:
        lines = f.readlines()

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i].strip()
        if line.startswith('cluster'):
            # record cluster identifier for messages
            parts = line.split(maxsplit=1)
            cluster_id = parts[1] if len(parts) > 1 else ''

            # reset block data
            sites_count = None
            state_entries = []
            site_types = []
            i += 1
            # parse cluster block
            while i < n and not lines[i].strip().startswith('end_cluster'):
                text = lines[i].strip()
                if text.startswith('sites'):
                    toks = text.split()
                    if len(toks) >= 2 and toks[1].isdigit():
                        sites_count = int(toks[1])
                if text.startswith('lattice_state'):
                    i += 1
                    count = 0
                    while i < n and count < (sites_count or float('inf')):
                        row = lines[i].strip()
                        if not row or row.startswith('#'):
                            i += 1
                            continue
                        key = row.split()[0]
                        if key in ('site_types', 'graph_multiplicity', 'cluster_eng', 'neighboring', 'angles'):
                            break
                        parts = row.split()
                        if parts and parts[0] == '&':
                            state_entries.append(None)
                        elif len(parts) >= 3 and parts[0].isdigit() and parts[2].isdigit():
                            spec = parts[1]
                            dent = int(parts[2])
                            state_entries.append((spec, dent))
                        i += 1
                        count += 1
                    continue
                if text.startswith('site_types'):
                    toks = text.split()
                    site_types = toks[1:]
                i += 1
            # reached end_cluster
            if sites_count is None:
                raise EnergeticsModelError(f"Missing 'sites' declaration in cluster '{cluster_id}'.")
            if len(site_types) != sites_count:
                raise EnergeticsModelError(
                    f"Cluster '{cluster_id}' declares {sites_count} sites but site_types has {len(site_types)} entries: {site_types}")
            if len(state_entries) != sites_count:
                raise EnergeticsModelError(
                    f"Cluster '{cluster_id}' declares {sites_count} sites but lattice_state provided {len(state_entries)} entries.")

            # build per-cluster mapping: species -> {dentate: site_type}
            cluster_map = {}
            for idx in range(sites_count):
                entry = state_entries[idx]
                stype = site_types[idx]
                if entry is None:
                    continue
                spec, dent = entry
                exp = species_dentates.get(spec)
                if exp is None:
                    raise EnergeticsModelError(
                        f"Species '{spec}' in cluster '{cluster_id}' not declared in simulation_input.dat.")
                if dent < 1 or dent > exp:
                    raise EnergeticsModelError(
                        f"Dentate index {dent} out of range for species '{spec}' in cluster '{cluster_id}' (expected 1..{exp}).")
                cluster_map.setdefault(spec, {})[dent] = stype
            # ensure full dentate coverage per species
            for spec, dent_dict in cluster_map.items():
                if len(dent_dict) != species_dentates[spec]:
                    raise EnergeticsModelError(
                        f"Species '{spec}' in cluster '{cluster_id}' has {species_dentates[spec]} dentates but got {len(dent_dict)} entries.")
            # merge into global mapping with order-flexible consistency
            for spec, dent_dict in cluster_map.items():
                if spec not in species_mapping:
                    species_mapping[spec] = dent_dict.copy()
                else:
                    existing_dict = species_mapping[spec]
                    if existing_dict != dent_dict:
                        # build ordered lists
                        existing_list = [existing_dict[d] for d in sorted(existing_dict)]
                        new_list = [dent_dict[d] for d in sorted(dent_dict)]
                        # same multiset? then warn and keep existing order
                        if sorted(existing_list) == sorted(new_list):
                            warnings.warn(
                                f"In cluster '{cluster_id}', dentates for species '{spec}' appear in {new_list} "
                                f"instead of {existing_list}; keeping original order.")
                        else:
                            raise EnergeticsModelError(
                                f"Inconsistent site types for species '{spec}' in cluster '{cluster_id}': "
                                f"{existing_list} vs {new_list}")
            i += 1  # skip end_cluster
        else:
            i += 1

    # finalize result
    result = {}
    for spec in surf_specs:
        if spec not in species_mapping:
            raise EnergeticsModelError(
                f"Species '{spec}' declared in simulation_input.dat but not found in energetics_input.dat.")
        dent_dict = species_mapping[spec]
        cnt = species_dentates[spec]
        sites = [None] * cnt
        for dent, stype in dent_dict.items():
            sites[dent - 1] = stype
        result[spec] = sites
    return result



def check_default_lattice(job_path: str = None, **kwargs):
    """
    Check whether the simulation uses a default lattice configuration.

    Parameters
    ----------
    job_path : str, optional
        The path to the directory containing the `lattice_input.dat` file.
        (Previously named 'path'.) For backward compatibility, you can pass 'path' instead.

    Returns
    -------
    bool
        True if the `lattice_input.dat` file indicates a default lattice configuration, False otherwise.
    """

    if job_path is None:
        job_path = kwargs.pop('path', None)
    if job_path is None:
        raise TypeError("Missing required argument: job_path (or 'path' for backwards compatibility)")

    with open(os.path.join(job_path, 'lattice_input.dat'), 'r') as file:
        for line in file:
            if 'lattice' in line and 'default_choice' in line:
                return True
    return False
