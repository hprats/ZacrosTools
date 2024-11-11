import functools
import inspect
from typing import Union, get_origin, get_args


class ZacrosToolsError(Exception):
    """Base class for exceptions in this library."""
    pass


class LatticeModelError(ZacrosToolsError):
    """Exception raised for errors in the lattice model."""
    pass


class GasModelError(ZacrosToolsError):
    """Exception raised for errors in the gas model."""
    pass


class EnergeticsModelError(ZacrosToolsError):
    """Exception raised for errors in the energetics model."""
    pass


class ReactionModelError(ZacrosToolsError):
    """Exception raised for errors in the reaction model."""
    pass


class KMCModelError(ZacrosToolsError):
    """Exception raised for errors when creating the KMC model."""
    pass


class CalcFunctionsError(ZacrosToolsError):
    """Exception raised for errors in the calc_functions module."""
    pass


class KMCOutputError(ZacrosToolsError):
    """Exception raised for errors in the kmc_output module."""
    pass


class PlotError(ZacrosToolsError):
    """Exception raised for errors in the plot_functions module."""
    pass


def enforce_types(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        signature = inspect.signature(func)
        bound_args = signature.bind(*args, **kwargs)
        for name, value in bound_args.arguments.items():
            expected_type = signature.parameters[name].annotation
            if expected_type != inspect.Parameter.empty:
                if get_origin(expected_type) is Union:
                    allowed_types = get_args(expected_type)
                else:
                    allowed_types = (expected_type,)
                if not any(isinstance(value, t) for t in allowed_types):
                    expected_types_str = ', '.join([t.__name__ for t in allowed_types])
                    raise TypeError(
                        f"Argument '{name}' must be one of types: {expected_types_str}; "
                        f"got {type(value).__name__} instead."
                    )
        return func(*args, **kwargs)

    return wrapper
