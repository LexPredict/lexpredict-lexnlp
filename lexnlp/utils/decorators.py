# pylint: disable=bare-except

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import types
from typing import Any, Callable


def safe_failure(func):
    """
    Return None on failure, either skip result if generator
    """
    def decorator(*args, **kwargs):
        raise_exc = not kwargs.pop('safe_failure', True)
        try:
            res = func(*args, **kwargs)
            if isinstance(res, types.GeneratorType):
                try:
                    yield from func(*args, **kwargs)
                except:
                    if raise_exc:
                        raise
        except:
            if raise_exc:
                raise
            return None
    return decorator


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
