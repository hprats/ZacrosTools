import pandas as pd
from zacrostools.kmc_model import KMCModel
from zacrostools.lattice_input import LatticeModel

gas_data = pd.read_csv("/Users/hprats/PycharmProjects/ZacrosTools/tests/input_files/gas_data.csv", index_col=0)
mechanism_data = pd.read_csv("/Users/hprats/PycharmProjects/ZacrosTools/tests/input_files/mechanism_data.csv", index_col=0)
energetics_data = pd.read_csv("/Users/hprats/PycharmProjects/ZacrosTools/tests/input_files/energetics_data.csv", index_col=0)
lattice_model = LatticeModel.from_file(path="/Users/hprats/PycharmProjects/ZacrosTools/tests/input_files/lattice_input.dat")

kmc_model = KMCModel(gas_data=gas_data,
                     mechanism_data=mechanism_data,
                     energetics_data=energetics_data,
                     lattice_model=lattice_model)

kmc_model.create_job_dir(path="/Users/hprats/PycharmProjects/ZacrosTools/tests/zacros_files",
                         temperature=1000,
                         pressure={'CO': 1.0})

