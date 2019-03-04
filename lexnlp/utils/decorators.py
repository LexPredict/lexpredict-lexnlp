# pylint: disable=bare-except

# Imports
import types

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def safe_failure(func):
    """
    return None on failure, either skip result if generator
    """
    def decorator(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
            if isinstance(res, types.GeneratorType):
                for i in res:
                    try:
                        yield i
                    except:
                        pass
        except:
            return None
    return decorator
