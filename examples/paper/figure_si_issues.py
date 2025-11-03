import numpy as np
import matplotlib.pyplot as plt
from zacrostools.kmc_output import KMCOutput

# Paths to the two simulations
paths = {
    'CH4_1e-4 # CO2_1e+0': (
        '/Users/hprats/PycharmProjects/tmc4mpo/wp4/kmc/'
        'tests_Pt/temp_1100_DRM_1100K/CH4_1.000e-04#CO2_1.000e+00'
    ),
    'CH4_3.162e-2 # CO2_1.931e-1': (
        '/Users/hprats/PycharmProjects/tmc4mpo/wp4/kmc/'
        'tests_Pt/temp_1100_DRM_1100K/CH4_3.162e-02#CO2_1.931e-01'
    )
}

# Analysis settings
analysis_full = [0, 100]   # for plotting
analysis_cut  = [20, 100]  # for metrics
range_type    = 'nevents'
weights       = 'time'

# Store plotting data
plot_data = {}

# Loop over each simulation
for label, path in paths.items():
    # 1) full range for plotting
    kmc_full = KMCOutput(
        path=path,
        analysis_range=analysis_full,
        range_type=range_type,
        weights=weights
    )
    x_full       = kmc_full.nevents
    energy_full  = kmc_full.energy
    time_full    = kmc_full.time

    # 2) cut range for metrics
    kmc_cut = KMCOutput(
        path=path,
        analysis_range=analysis_cut,
        range_type=range_type,
        weights=weights
    )
    x_cut      = kmc_cut.nevents
    energy_cut = kmc_cut.energy
    time_cut   = kmc_cut.time

    # Compute energy slope on 20–100%
    coeffs_e = np.polyfit(x_cut, energy_cut, 1)
    slope_e  = coeffs_e[0]

    # Compute time vs events R² on 20–100%
    coeffs_t   = np.polyfit(x_cut, time_cut, 1)
    time_pred  = coeffs_t[0] * x_cut + coeffs_t[1]
    r2_time    = np.corrcoef(time_cut, time_pred)[0, 1]**2

    print(f"{label}\n"
          f"  → Energy slope (20–100%): {slope_e:.2e} eV/Å² per event\n"
          f"  → Time vs events R² (20–100%): {r2_time:.4f}\n")

    # Save for plotting
    plot_data[label] = (x_full, energy_full, time_full, x_cut[0])

# Create 2×2 figure
fig, axes = plt.subplots(2, 2, figsize=(6, 5))

for col, label in enumerate(paths):
    x, y_e, y_t, cutoff = plot_data[label]

    # Top: energy vs events
    ax_e = axes[0, col]
    ax_e.plot(x, y_e, linewidth=2)
    ax_e.axvline(cutoff, color='red', linestyle='--',
                 label='20 % cutoff')
    #ax_e.set_ylabel('Lattice energy (eV/Å²)')
    if col == 0:
        ax_e.legend(fontsize=8)

    # Bottom: time vs events
    ax_t = axes[1, col]
    ax_t.plot(x, y_t, linewidth=2)
    ax_t.axvline(cutoff, color='red', linestyle='--')
    #ax_t.set_xlabel('Number of events')
    #ax_t.set_ylabel('Simulated time (s)')
    ax_t.ticklabel_format(axis='x', scilimits=[-2, 3], useOffset=True)

plt.tight_layout()
plt.savefig(
    '/Users/hprats/Desktop/energy_time_comparison.pdf',
    bbox_inches='tight',
    transparent=True
)
plt.show()
