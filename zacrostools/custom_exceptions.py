import functools
import inspect


class KMCModelError(Exception):
    """Base class for exceptions in this module."""
    pass


class LatticeModelError(KMCModelError):
    """Exception raised for errors in the lattice model."""
    pass


class ReactionModelError(KMCModelError):
    """Exception raised for errors in the reaction model."""
    pass


class EnergeticModelError(KMCModelError):
    """Exception raised for errors in the energetic model."""
    pass


class InconsistentDataError(KMCModelError):
    """Exception raised for inconsistent data across models."""
    pass


def enforce_types(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        signature = inspect.signature(func)
        bound_args = signature.bind(*args, **kwargs)
        for name, value in bound_args.arguments.items():
            expected_type = signature.parameters[name].annotation
            if expected_type != inspect.Parameter.empty and not isinstance(value, expected_type):
                raise TypeError(f"Argument '{name}' must be of type {expected_type.__name__}")
        return func(*args, **kwargs)

    return wrapper
