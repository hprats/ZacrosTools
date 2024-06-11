import sys
import numpy as np
from zacrostools.analysis_functions import get_data_general, get_data_specnum


class KMCOutput:
    """A class that represents a KMC output."""

    def __init__(self, path, ignore=0.0, coverage_per_site=False, ads_sites=None):
        self.path = path

        # Get data from general_output.txt file
        data_general = get_data_general(path)
        self.n_gas_species = data_general['n_gas_species']
        self.gas_species_names = data_general['gas_species_names']
        self.n_surf_species = data_general['n_surf_species']
        self.surf_species_names = data_general['surf_species_names']
        self.n_sites = data_general['n_sites']
        self.area = data_general['area']
        self.site_types = data_general['site_types']

        # Get data from specnum_output.txt
        data_specnum, header = get_data_specnum(path, ignore)
        self.time = data_specnum[:, 2]
        self.final_time = data_specnum[-1, 2]
        self.final_energy = data_specnum[-1, 4] / self.area
        self.energy = np.average(data_specnum[:, 4]) / self.area

        # Production (molec) and TOF (molec/s-1/Å2)
        self.production = {}
        self.av_production = {}  # needed for selectivity
        self.tof = {}
        for i in range(5 + self.n_surf_species, len(header)):
            ads = header[i]
            self.production[ads] = data_specnum[:, i]
            self.av_production[ads] = data_specnum[-1, i] - data_specnum[0, i]
            if data_specnum[-1, i] != 0:
                self.tof[header[i]] = np.polyfit(data_specnum[:, 2], data_specnum[:, i], 1)[0] / self.area
            else:
                self.tof[header[i]] = 0.00

        # Coverage (%)
        self.coverage = {}
        self.av_coverage = {}
        for i in range(5, 5 + self.n_surf_species):
            ads = header[i].replace('*', '')
            self.coverage[ads] = data_specnum[:, i] / self.n_sites * 100
            self.av_coverage[ads] = np.average(data_specnum[:, i]) / self.n_sites * 100
        self.total_coverage = sum(self.coverage.values())
        self.av_total_coverage = sum(self.av_coverage.values())
        self.dominant_ads = max(self.av_coverage, key=self.av_coverage.get)

        # Coverage per site type (%)
        if len(self.site_types) == 1:
            print("ERROR: coverage_per_site not available when there is only one site type")
            sys.exit(f"path: {self.path}")
        if coverage_per_site:
            self.coverage_per_site_type = {}
            self.av_coverage_per_site_type = {}
            for site_type in self.site_types:
                self.coverage_per_site_type[site_type] = {}
                self.av_coverage_per_site_type[site_type] = {}
            for i in range(5, 5 + self.n_surf_species):
                ads = header[i].replace('*', '')
                site_type = ads_sites[ads]
                self.coverage_per_site_type[site_type][ads] = data_specnum[:, i] / self.site_types[ads_sites[ads]] * 100
                self.av_coverage_per_site_type[site_type][ads] = np.average(data_specnum[:, i]) / self.site_types[
                    ads_sites[ads]] * 100
            self.total_coverage_per_site_type = {}
            self.av_total_coverage_per_site_type = {}
            self.dominant_ads_per_site_type = {}
            for site_type in self.site_types:
                self.total_coverage_per_site_type[site_type] = sum(self.coverage_per_site_type[site_type].values())
                self.av_total_coverage_per_site_type[site_type] = sum(
                    self.av_coverage_per_site_type[site_type].values())
                self.dominant_ads_per_site_type[site_type] = max(self.av_coverage_per_site_type[site_type],
                                                                 key=self.av_coverage_per_site_type[site_type].get)

    def get_selectivity(self, main_product, side_products):
        selectivity = float('NaN')
        tof_side_products = 0.0
        for side_product in side_products:
            tof_side_products += self.tof[side_product]
        if self.tof[main_product] + tof_side_products != 0:
            selectivity = self.tof[main_product] / (self.tof[main_product] + tof_side_products) * 100
        return selectivity
