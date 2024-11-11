from zacrostools.energetics_model import EnergeticsModel


energetics_model = EnergeticsModel.from_csv(csv_path='energetics_data.csv')

energetics_model.write_energetics_input(output_dir='.', sig_figs_energies=3)
