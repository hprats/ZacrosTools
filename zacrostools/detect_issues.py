import numpy as np
from zacrostools.kmc_output import KMCOutput


def detect_issues(path, window_percent):

    energy_slope_threshold = 5.0e-10  # eV/Å²/step
    time_linear_fit_threshold = 0.95

    def reduce_size(time, energy, nevents, size=100):
        if len(nevents) <= size:
            return time, energy, nevents
        else:
            indices = np.round(np.linspace(0, len(nevents) - 1, size)).astype(int)
            return time[indices], energy[indices], nevents[indices]

    kmc_output = KMCOutput(path=path, window_percent=window_percent,
                           window_type='nevents', weights='nevents')

    # Reduce arrays to 100 elements if necessary
    time_reduced, energy_reduced, nevents_reduced = reduce_size(time=kmc_output.time,
                                                                energy=kmc_output.energy,
                                                                nevents=kmc_output.nevents)

    # Check for a positive or negative trend in energy using linear regression
    coeffs_energy = np.polyfit(nevents_reduced, energy_reduced, 1)
    slope_energy = coeffs_energy[0]
    energy_trend = abs(slope_energy) > energy_slope_threshold

    # Perform linear regression on time vs. nevents
    coeffs_time = np.polyfit(nevents_reduced, time_reduced, 1)
    slope_time = coeffs_time[0]
    intercept_time = coeffs_time[1]
    time_predicted = slope_time * nevents_reduced + intercept_time
    r_squared_time = np.corrcoef(time_reduced, time_predicted)[0, 1] ** 2
    time_not_linear = r_squared_time < time_linear_fit_threshold

    # Detect issues
    has_issues = energy_trend or time_not_linear

    return has_issues
