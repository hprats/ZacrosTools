import pandas as pd
from zacrostools.energetics_model import EnergeticsModel


clusters = {
    'CO_point': {
        'site_types': 'tC',
        'lattice_state': ['1 CO* 1'],
        'cluster_eng': 0.233
    },
    'CO+CO_pair': {
        'site_types': 'tC tC',
        'neighboring': '1-2',
        'lattice_state': ['1 CO* 1', '2 CO* 1'],
        'cluster_eng': 0.177
    }
}


energetics_data = pd.DataFrame.from_dict(clusters, orient='index')

try:
    energetics_model = EnergeticsModel.from_df(energetics_data)
    energetics_model.write_energetics_input(output_dir='.', sig_figs_energies=3)
except Exception as e:
    print(f"Error creating EnergeticsModel: {e}")
