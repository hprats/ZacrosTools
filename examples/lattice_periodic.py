from zacrostools.lattice_model import LatticeModel


lattice_model = LatticeModel(lattice_type='periodic_cell',
                             cell_vectors=((3.27, 0), (0, 3.27)),
                             sites={'tC': (0.25, 0.25), 'tM': (0.75, 0.75)},
                             copies=[2, 2],
                             neighboring_structure='from_distances',
                             max_distances={'tC-tC': 4.0, 'tC-tM': 4.0, 'tM-tM': 4.0, 'Pt-Pt': 4.0, 'Pt-tC': 4.0, 'Pt-tM': 4.0},
                             )

lattice_model.repeat_lattice_model(4, 4)

# replace 4 tC sites by Pt
for coordinates in [(0.3125, 0.3125), (0.3125, 0.5625), (0.5625, 0.3125), (0.5625, 0.5625)]:
    lattice_model.change_site_type(direct_coords=coordinates, new_site_type='Pt')

# remove the tM site in the middle
lattice_model.remove_site(direct_coords=(0.4375, 0.4375))

lattice_model.write_lattice_input(output_dir='.', sig_figs=4)
