import functools
import logging
from typing import Callable

# Global dictionary of function pointers
_FUNCTION_POINTERS = {}


def on_first_time(intro: Callable) -> Callable[[Callable], Callable]:
    """
    Decorator to inject an "intro" callable the first time
    the decorated function is called

    :param intro: Callable without arguments
    :return: decorator
    """

    def decorator(f: Callable):
        # Instead of spending time and state on counting and
        # `if first do this else that` constructs
        # we try to be more efficient by using a "function pointer" swap trick.
        # We initialize the function pointer with a "first time"
        # version that executes `intro`, the original decorated function `f`,
        # and directly sets the pointer to the to just `f`,
        # so that subsequent calls don't do `intro` anymore.
        # Also note that we use global state `_FUNCTION_POINTERS`
        # instead of closure level state because the latter is not
        # updated appropriately in PySpark's driver-executor round trip.

        key = id(f)

        def first_time(*args, **kwargs):
            # Reset function pointer to original decorated function
            _FUNCTION_POINTERS[key] = f
            # Call intro and original function
            intro()
            return f(*args, **kwargs)

        # Initialize with "first time" version
        _FUNCTION_POINTERS[key] = first_time

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            return _FUNCTION_POINTERS[key](*args, **kwargs)

        return wrapper

    return decorator


def ensure_basic_logging(f=None, **kwargs) -> Callable:
    """
    Decorator to ensure that `logging.basicConfig` is called
    when the decorated function is called for the first time.
    """
    decorator = on_first_time(lambda: logging.basicConfig(**kwargs))
    # Was decorator used without parenthesis or parameterized?
    return decorator(f) if callable(f) else decorator
