import numpy as np
from zacrostools.kmc_output import KMCOutput


def detect_issues(path,
                  analysis_range,
                  energyslope_threshold=5.0e-10,
                  time_linear_fit_threshold=0.95,
                  max_points=100):
    """
    Detect issues in a KMC simulation by analyzing the energy slope and
    the linearity of time with respect to the number of events.

    A simulation that has reached a steady state is characterized by:
    - A low absolute energy slope over KMC events (energy fluctuates around a stable value).
    - A strong linear correlation between simulated time and the number of KMC events.

    Parameters
    ----------
    path : str
        Path to the directory containing KMC simulation output.
    analysis_range : tuple or list of int
        Range of KMC events to analyze (e.g., (0, 10000)).
    energyslope_threshold : float, optional
        Threshold for the absolute energy slope (in eV/Å²/step) above
        which the simulation is considered to have an issue, by default 5.0e-10.
    time_linear_fit_threshold : float, optional
        Threshold for the R² value in the time vs. KMC events regression,
        by default 0.95. If the R² is below this value, the simulation is
        considered to have an issue.
    max_points : int, optional
        Maximum number of data points to use in the regression. If the data
        arrays are longer, they will be uniformly sampled down to this length,
        by default 100.
    """

    def reduce_size(time, energy, nevents, size):
        """
        Uniformly sample the data arrays down to a specified size.
        """
        length = len(nevents)
        if length <= size:
            return time, energy, nevents

        indices = np.round(np.linspace(0, length - 1, size)).astype(int)
        return time[indices], energy[indices], nevents[indices]

    # Get simulation data
    kmc_output = KMCOutput(path=path, analysis_range=analysis_range,
                           range_type='nevents', weights='nevents')

    # Reduce arrays if necessary
    time_reduced, energy_reduced, nevents_reduced = reduce_size(kmc_output.time,
                                                               kmc_output.energy,
                                                               kmc_output.nevents,
                                                               max_points)

    # Edge-case check: Need at least 2 data points to perform any linear regression
    if len(nevents_reduced) < 2:
        raise ValueError("Not enough data points to perform regression. "
                         f"Got {len(nevents_reduced)} points.")

    # Check for trend in energy using linear regression
    coeffs_energy = np.polyfit(nevents_reduced, energy_reduced, 1)
    slope_energy = coeffs_energy[0]
    energy_trend = abs(slope_energy) > energyslope_threshold

    # Perform linear regression on time vs. nevents
    coeffs_time = np.polyfit(nevents_reduced, time_reduced, 1)
    slope_time = coeffs_time[0]
    intercept_time = coeffs_time[1]
    time_predicted = slope_time * nevents_reduced + intercept_time

    # Compute R² for the time vs. nevents regression
    r_squared_time = np.corrcoef(time_reduced, time_predicted)[0, 1] ** 2
    time_not_linear = r_squared_time < time_linear_fit_threshold

    # If either the energy slope is too large or time is not linear, flag issues
    has_issues = energy_trend or time_not_linear

    return has_issues
