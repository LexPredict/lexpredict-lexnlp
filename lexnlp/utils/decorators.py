# pylint: disable=bare-except

# Imports

import types

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def safe_failure(func):
    """
    return None on failure, either skip result if generator
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
