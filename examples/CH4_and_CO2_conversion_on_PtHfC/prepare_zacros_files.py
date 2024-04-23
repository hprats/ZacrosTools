import os
import numpy as np
import pandas as pd
from zacrostools.kmc_model import KMCModel
from zacrostools.lattice_input import LatticeModel

catalyst = 'PtHfC'  # PtHfC or HfC
reaction = 'DRM'  # DRM, SRM, POM, WGS or RWGS
temperature = 1000  # in K
grid_points_pX = 15
grid_points_pY = 15

repeat_cell = {'HfC': [10, 10], 'PtHfC': [3, 3]}

df_mechanism = pd.read_csv(f'mechanism.csv', index_col=0)
df_energetics = pd.read_csv(f'energetics.csv', index_col=0)
lattice_model = LatticeModel.from_file(path=f"lattice_input_{catalyst}.dat")
lattice_model.repeat_cell(repeat_cell[catalyst])

if catalyst == 'HfC':  # remove steps and clusters involving the Pt cluster
    for cluster in df_energetics.index:
        if 'Pt' in cluster:
            df_energetics = df_energetics.drop(cluster)
    for step in df_mechanism.index:
        if 'Pt' in step:
            df_mechanism = df_mechanism.drop(step)

job = KMCModel(gas_data=pd.read_csv(f'gas_data.csv', index_col=0),
               mechanism_data=df_mechanism,
               energetics_data=df_energetics,
               lattice_model=lattice_model)

scan_path = f"scan_{catalyst}_{reaction}_{temperature}K"
if not os.path.exists(scan_path):
    os.mkdir(scan_path)

reactions = {
    'DRM': {'reactants': ['CH4', 'CO2'], 'products': ['CO', 'H2', 'H2O', 'O2'], 'logpX_min': -3, 'logpY_min': -5},
    'SRM': {'reactants': ['CH4', 'H2O'], 'products': ['CO', 'H2', 'CO2', 'O2'], 'logpX_min': -3, 'logpY_min': -6},
    'POM': {'reactants': ['CH4', 'O2'], 'products': ['CO', 'H2', 'H2O', 'CO2'], 'logpX_min': -3, 'logpY_min': -8},
    'WGS': {'reactants': ['CO', 'H2O'], 'products': ['CO2', 'H2', 'CH4', 'O2'], 'logpX_min': -3, 'logpY_min': -7},
    'RWGS': {'reactants': ['CO2', 'H2'], 'products': ['CO', 'H2O', 'CH4', 'O2'], 'logpX_min': -5, 'logpY_min': -4}}

# List of processes that would be stiffness scalable
auto_scaling = ['fH2O', 'bCH3', 'bCH2', 'bCH']
for step in df_mechanism.index:
    if step[0] == 'a':  # Include reactant adsorption steps
        if step.replace('_HfC', '').replace('_Pt', '')[1:] in reactions[reaction]['reactants']:
            auto_scaling.append(step)  # add reactant steps
    elif step[0] == 'd':  # Include all diffusion steps within the HfC region
        if '_HfC' in step:
            auto_scaling.append(step)


for pX in np.logspace(reactions[reaction]['logpX_min'], reactions[reaction]['logpX_min'] + 5, grid_points_pX):
    for pY in np.logspace(reactions[reaction]['logpY_min'], reactions[reaction]['logpY_min'] + 5, grid_points_pY):
        pressure = {reactions[reaction]['reactants'][0]: pX, reactions[reaction]['reactants'][1]: pY}
        for molecule in reactions[reaction]['products']:
            pressure[molecule] = 0.0
        folder_name = f"{reactions[reaction]['reactants'][0]}_{pX:.3e}#{reactions[reaction]['reactants'][1]}_{pY:.3e}"
        path = f'{scan_path}/{folder_name}'
        job.create_job_dir(path=path,
                           temperature=temperature,
                           pressure=pressure,
                           report='on event 100000',
                           stop={'max_steps': 'infinity', 'max_time': 50000, 'wall_time': 172800},
                           auto_scaling=auto_scaling)
