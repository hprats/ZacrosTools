import pandas as pd

gas_molecules = {
    'CO': {'type': 'linear',
           'gas_molec_weight': 28.01,
           'sym_number': 1,
           'degeneracy': 1,
           'inertia_moments': [8.973619026272551],
           'gas_energy': 1.96}
}

steps = {
    'CO_adsorption': {
        'sites': 1,
        'site_types': 'topC',
        'neighboring': '',
        'area_site': 5.34,
        'initial': ['1 * 1'],
        'final': ['1 CO* 1'],
        'activ_eng': 0.0,
        'molecule': 'CO',
        'vib_energies_is': [264.160873],
        'vib_energies_fs': [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359],
        'prox_factor': 0.0},
    'CO_diffusion': {
        'sites': 1,
        'site_types': 'topC',
        'neighboring': '',
        'area_site': 5.34,
        'initial': ['1 * 1'],
        'final': ['1 CO* 1'],
        'activ_eng': 0.0,
        'molecule': 'CO',
        'vib_energies_is': [264.160873],
        'vib_energies_fs': [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359],
        'vib_energies_ts': [240.497465, 82.738219, 60.132962, 60.080258, 7.271753],
        'prox_factor': 0.0},
}

clusters = {
    'CO_point': {
        'site_types': 'tC',
        'lattice_state': ['1 CO* 1'],
        'cluster_eng': 0.233},
    'CO+CO_pair': {
        'site_types': 'tC tC',
        'neighboring': '1-2',
        'lattice_state': ['1 CO* 1', '2 CO* 1'],
        'cluster_eng': 0.177}
}

gas_data = pd.DataFrame(gas_molecules).T
mechanism_data = pd.DataFrame(steps).T
energetics_data = pd.DataFrame(clusters).T

gas_data.to_csv("/Users/hprats/PycharmProjects/ZacrosTools/tests/input_files/gas_data.csv")
mechanism_data.to_csv("/Users/hprats/PycharmProjects/ZacrosTools/tests/input_files/mechanism_data.csv")
energetics_data.to_csv("/Users/hprats/PycharmProjects/ZacrosTools/tests/input_files/energetics_data.csv")


