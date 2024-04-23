import numpy as np


def find_nearest(array, value):
    """Finds the element of an array whose value is closest to a given value, and returns its index.

    Parameters
    ----------
    array: np.Array
    value: float

    Returns
    -------
    array[idx]: int

    """
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]



