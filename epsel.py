import functools
import logging
from typing import Callable


def on_first_time(intro: Callable) -> Callable[[Callable], Callable]:
    """
    Decorator to inject an "intro" callable the first time
    the decorated function is called

    :param intro: Callable without arguments
    :return: decorator
    """

    def decorator(f: Callable):
        # Instead of doing some kind of `if first do this else that`
        # construct that has to be executed each call, we try to be
        # more efficient by using a "function pointer" trick.
        # Initially, this `ptr` variable is a function that executes
        # the `intro` callable and original decorated function `f`,
        # but it also (re)sets `ptr` to just `f`, so that subsequent
        # calls don't do `intro` anymore.

        def ptr(*args, **kwargs):
            # Reset function pointer to original decorated function
            nonlocal ptr
            ptr = f
            # Call intro and original function
            intro()
            return f(*args, **kwargs)

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            return ptr(*args, **kwargs)

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
