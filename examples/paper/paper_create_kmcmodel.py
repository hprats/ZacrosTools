from zacrostools.kmc_model import KMCModel
from zacrostools.gas_model import GasModel
from zacrostools.reaction_model import ReactionModel
from zacrostools.energetics_model import EnergeticsModel
from zacrostools.lattice_model import LatticeModel

lattice_model = LatticeModel(
    lattice_type='default_choice',
    default_lattice_type='hexagonal_periodic',
    lattice_constant=2.5,
    copies=[10, 10]
)

gas_model = GasModel.from_dict({
    'CO': {
        'type': 'linear',
        'sym_number': 1,
        'inertia_moments': [8.973],
        'gas_energy': 1.954}
})

energetics_model = EnergeticsModel.from_dict({
    'CO_point': {
        'cluster_eng': 0.230,
        'lattice_state': ['1 CO* 1']},
    'CO+CO_pair': {
        'cluster_eng': 0.177,
        'lattice_state': ['1 CO* 1', '2 CO* 1'],
        'neighboring': '1-2',
        'graph_multiplicity': 2.0}
})

reaction_model = ReactionModel.from_dict({
    'CO_adsorption': {
        'activ_eng': 0.0,
        'area_site': 5.34,
        'final': ['1 CO* 1'],
        'initial': ['1 * 1'],
        'molecule': 'CO',
        'prox_factor': 0.0,
        'vib_energies_fs': [240, 82, 60, 60, 7, 7],
        'vib_energies_is': [263]},
    'CO_diffusion': {
        'activ_eng': 1.156,
        'final': ['1 * 1', '2 CO* 1'],
        'initial': ['1 CO* 1', '2 * 1'],
        'neighboring': '1-2',
        'graph_multiplicity': 2.0,
        'vib_energies_fs': [240, 82, 60, 60, 7, 7],
        'vib_energies_is': [240, 82, 60, 60, 7, 7],
        'vib_energies_ts': [218, 53, 47, 28, 7]}
})

kmc_model = KMCModel(
    lattice_model=lattice_model,
    gas_model=gas_model,
    reaction_model=reaction_model,
    energetics_model=energetics_model)