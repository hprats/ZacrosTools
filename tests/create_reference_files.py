from zacrostools.kmc_model import KMCModel
from zacrostools.gas_model import GasModel
from zacrostools.energetics_model import EnergeticsModel
from zacrostools.reaction_model import ReactionModel
from zacrostools.lattice_model import LatticeModel

gas_model = GasModel.from_csv(csv_path='csv_files_for_tests/gas_model.csv')
energetics_model = EnergeticsModel.from_csv(csv_path='csv_files_for_tests/energetics_model.csv')
reaction_model = ReactionModel.from_csv(csv_path='csv_files_for_tests/reaction_model.csv')
lattice_model = LatticeModel(lattice_type='periodic_cell',
                             cell_vectors=((3.27, 0), (0, 3.27)),
                             sites={'tC': (0.25, 0.25), 'tM': (0.75, 0.75)},
                             copies=[10, 10],
                             neighboring_structure='from_distances',
                             max_distances={'tC-tC': 4.0, 'tC-tM': 4.0, 'tM-tM': 4.0, 'Pt-Pt': 4.0, 'Pt-tC': 4.0,
                                            'Pt-tM': 4.0},
                             )
lattice_model.repeat_lattice_model(4, 4)
for coordinates in [(0.3125, 0.3125), (0.3125, 0.5625), (0.5625, 0.3125), (0.5625, 0.5625)]:
    lattice_model.change_site_type(direct_coords=coordinates, new_site_type='Pt')
lattice_model.remove_site(direct_coords=(0.4375, 0.4375))
lattice_model.copies = [2, 2]

kmc_model = KMCModel(
    gas_model=gas_model,
    reaction_model=reaction_model,
    energetics_model=energetics_model,
    lattice_model=lattice_model)

stiffness_scalable_steps = [
    'aCH4_HfC', 'aCH4_Pt-1', 'aCH4_Pt-2', 'aCH4_in-1', 'aCH4_in-2',
    'aCO2_HfC', 'aCO2_Pt', 'bCH3_HfC', 'bCH3_Pt-1', 'bCH3_Pt-2',
    'bCH3_in-1', 'bCH3_in-2', 'bCH2_HfC', 'bCH2_in-1', 'bCH2_in-2',
    'bCH_HfC', 'bCH_in-1', 'bCH_in-2', 'bCH_in-3', 'bCH_in-4',
    'fCO_HfC', 'fCO_in-1', 'fCO_in-2', 'fCO_in-3', 'fCO_in-4',
    'CHtoCHO_HfC', 'CHtoCHO_in-1', 'CHtoCHO_in-2', 'CHtoCHO_in-3',
    'CHtoCHO_in-4', 'CHOtoCO_HfC', 'CHOtoCO_Pt-1', 'CHOtoCO_Pt-2',
    'CHOtoCO_in-1', 'CHOtoCO_in-2', 'CtoCOH_HfC', 'CtoCOH_in-1',
    'CtoCOH_in-2', 'COHtoCHO_HfC', 'COHtoCHO_Pt', 'bCO2_HfC',
    'bCO2_Pt', 'bCO2_in', 'fOH_HfC', 'fOH_Pt-1', 'fOH_Pt-2',
    'fOH_in_a-1', 'fOH_in_a-2', 'fOH_in_b-1', 'fH2O_HfC',
    'fH2O_Pt-1', 'fH2O_Pt-2', 'fH2O_in-1', 'fH2O_in-2',
    'CO2toCOOH_HfC', 'CO2toCOOH_Pt', 'CO2toCOOH_in-1',
    'CO2toCOOH_in-2', 'COOHtoCO_HfC', 'COOHtoCO_Pt-1',
    'COOHtoCO_Pt-2', 'COOHtoCO_in-1', 'COOHtoCO_in-2',
    'dO_in-1', 'dO_in-2', 'dH_in', 'dCO_in', 'dOH_in',
    'dH2O_in', 'dCH2_in-1', 'dCH2_in-2', 'dCH_in-1',
    'dCH_in-2', 'dCH_in-3', 'dCH_in-4', 'dCHO_in-1',
    'dCHO_in-2', 'dCOH_in-1', 'dCOH_in-2'
]

stiffness_scalable_symmetric_steps = [
    'dO_HfC', 'dH_HfC', 'dCO_HfC', 'dOH_HfC', 'dH2O_HfC',
    'dCH3_HfC', 'dCH2_HfC', 'dCH_HfC', 'dC_HfC', 'dCHO_HfC',
    'dCOH_HfC', 'dO_Pt', 'dH_Pt', 'dCO_Pt', 'dOH_Pt',
    'dH2O_Pt', 'dCH3_Pt', 'dCH2_Pt', 'dCHO_Pt', 'dCOH_Pt'
]

pressure = {'CH4': 0.0001, 'CO2': 1.0, 'CO': 0.0, 'H2': 0.0, 'H2O': 0.0, 'O2': 0.0}

reporting_scheme = {'snapshots': 'on event 100000',
                    'process_statistics': 'on event 100000',
                    'species_numbers': 'on event 100000'}

stopping_criteria = {'max_steps': 'infinity', 'max_time': 5.0e+06, 'wall_time': 172000}

auto_scaling_tags = {'check_every': 500000,
                     'min_separation': 50.0,
                     'max_separation': 100.0,
                     'tol_part_equil_ratio': 0.05,
                     'upscaling_factor': 5.0,
                     'upscaling_limit': 100.0,
                     'downscaling_limit': 2.0,
                     'min_noccur': 10}

kmc_model.create_job_dir(job_path='reference_files',
                         temperature=1000,
                         pressure=pressure,
                         reporting_scheme=reporting_scheme,
                         stopping_criteria=stopping_criteria,
                         stiffness_scaling_algorithm='prats2024',
                         stiffness_scalable_steps=stiffness_scalable_steps,
                         stiffness_scalable_symmetric_steps=stiffness_scalable_symmetric_steps,
                         stiffness_scaling_tags=auto_scaling_tags,
                         sig_figs_energies=3,
                         sig_figs_pe=3)
