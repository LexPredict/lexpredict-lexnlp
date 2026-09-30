__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from functools import wraps
from inspect import isgeneratorfunction
from typing import Any, Callable


def safe_failure(func):
    """
    Suppress ordinary failures unless ``safe_failure=False``.

    Scalar functions remain scalar and generator functions remain generators.
    Process-control exceptions such as ``KeyboardInterrupt`` and ``SystemExit``
    are deliberately not suppressed.
    """
    if isgeneratorfunction(func):
        @wraps(func)
        def generator_wrapper(*args, **kwargs):
            raise_exc = not kwargs.pop('safe_failure', True)
            try:
                yield from func(*args, **kwargs)
            except Exception:
                if raise_exc:
                    raise

        return generator_wrapper

    @wraps(func)
    def scalar_wrapper(*args, **kwargs):
        raise_exc = not kwargs.pop('safe_failure', True)
        try:
            return func(*args, **kwargs)
        except Exception:
            if raise_exc:
                raise
            return None

    return scalar_wrapper


def handle_invalid_text(
    _function: Callable = None,
    *,
    return_value: Any = None,
    failure_condition: Callable = lambda text: len(text) == 0,
) -> Any:
    """
    Return a given value if the `text` parameter of the decorated function
    meets the `failure_condition`.
    """
    def decorator(function):
        def wrapper(text, *args, **kwargs):
            if failure_condition(text):
                return return_value
            return function(text, *args, **kwargs)
        return wrapper

    if _function is None:
        return decorator
    return decorator(_function)
