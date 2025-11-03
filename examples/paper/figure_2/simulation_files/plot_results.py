import sys
import numpy as np
import matplotlib.pyplot as plt

# Read information from general_output.txt
n_surf_species = 0
n_sites = 0
area = 0
with open("general_output.txt", "r") as infile:
    lines = infile.readlines()
for line in lines:
    if 'Number of surface species' in line:
        n_surf_species = int(line.split()[-1])
    if 'Total number of lattice sites' in line or 'Number of lattice sites' in line:
        n_sites = float(line.split()[-1])
    if 'Lattice surface area' in line or 'Surface area' in line:
        area = float(line.split()[-1]) 
if n_surf_species == 0 or area == 0 or n_sites == 0:
    sys.exit("Problem reading information from general_output.txt")

# Read information from specnum_output.txt
with open("specnum_output.txt", "r") as infile:
    header = infile.readline().split()
data = np.loadtxt("specnum_output.txt", skiprows=1)

# Remove data corresponding to the equilibration phase
initial_time = float(input("\nChose initial time for computing averages (in s): "))
initial_row = -1
for i in range(len(data)):
    if data[i, 2] >= initial_time:
        initial_row = i
        break
if initial_row == -1:
    sys.exit("The chosen initial time is higher than the simulated time")
data = np.delete(data, np.s_[0:initial_row], axis=0)

# Print process statistics
print("\nProcess statistics (num. events): \n")
with open("procstat_output.txt", "r") as infile:
    lines = infile.readlines()
proc_header = lines[0].split()
num_events = lines[-1].split()
for i in range(len(proc_header)):
    print(f"{proc_header[i]}: {num_events[i]}")

# Plot surface coverage 
time = data[:, 2]
fig, axes = plt.subplots(2, 1, figsize=(3.5, 5), sharex=True)
print("\nSurface coverage (%): \n")
for i in range(5, 5 + n_surf_species):
    average_coverage = np.average(data[:, i]) / n_sites * 100
    print(f"{header[i]}: {average_coverage:.2f}")
    if average_coverage >= 1.00:
    #if np.max(data[:, i]) > 0:
        coverage = data[:, i] / n_sites * 100
        axes[0].plot(time, coverage, label=header[i])

# Plot TOF
print("\nTOF (molec·s-1·Å-2): \n")
for i in range(5 + n_surf_species, len(header)):
    tof = np.polyfit(time, data[:, i], 1)[0] / area  # tof
    print(f"{header[i]}: {tof:.2e}")
    if tof > 0.0 and data[-1, i] > 0:
        num_molecules = data[:, i]
        axes[1].plot(time, num_molecules, linewidth=2, label=header[i] + '$_{(g)}$')
for ax in axes:
    ax.legend(fontsize=8)
axes[0].set_ylabel('Coverage (%)')
axes[1].set_ylabel('Number of molecules')
axes[1].set_xlabel('Simulated time (s)')
axes[1].ticklabel_format(axis='x', scilimits=[-2, 3], useOffset=True)
plt.tight_layout()
plt.savefig("kmc_results.pdf", bbox_inches='tight', transparent=True)
plt.show()
