__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import numbers


def values_look_equal(a, b) -> bool:
    if a == b:
        return True

    if (isinstance(a, str) and not a and not b) or (isinstance(b, str) and not b and not a):
        return True

    if isinstance(a, numbers.Number) and isinstance(b, numbers.Number):
        a = float(a)
        b = float(b)

        delta = abs(a - b)
        da = 0 if a == 0 else 100 * delta / abs(a)
        db = 0 if b == 0 else 100 * delta / abs(b)
        dmax = max(da, db)
        # delta less than 0.001%
        return dmax < 0.001

    try:
        sa = str(a)
        sb = str(b)
        if sa == sb:
            return True
    except:  # pylint:disable=bare-except
        pass
    return False
