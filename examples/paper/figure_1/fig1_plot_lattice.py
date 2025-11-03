import matplotlib.pyplot as plt
from zacrostools.plot_periodic_lattice import plot_periodic_lattice

site_styles = {
    'tM': {'color': 'dodgerblue', 'marker': 'o', 'size': 250},
    'tC': {'color': 'grey', 'marker': 'o', 'size': 150},
    'Pt': {'color': 'silver', 'marker': 's', 'size': 200}
}

fig1, ax = plt.subplots(1, figsize=(1.6, 1.6))
plot_periodic_lattice(
    filename='hfc_lattice/lattice_input.dat',
    ax=ax,
    site_styles=site_styles,
    line_width=1.5)
plt.tight_layout()
plt.savefig('/Users/hprats/Desktop/hfc_lattice.pdf', bbox_inches='tight', transparent=True)

fig2, ax = plt.subplots(1, figsize=(3, 3))
plot_periodic_lattice(
    filename="pthfc_lattice/lattice_input.dat",
    ax=ax,
    site_styles=site_styles,
    line_width=1.5)
plt.tight_layout()
plt.savefig('/Users/hprats/Desktop/pthfc_lattice.pdf', bbox_inches='tight', transparent=True)

plt.show()
