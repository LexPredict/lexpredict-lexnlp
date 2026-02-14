__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from lexnlp.extract.en.addresses.addresses import get_address_spans, _safe_index
from lexnlp.tests import lexnlp_tests


def test_get_address():
    lexnlp_tests.test_extraction_func_on_test_data(func=get_address_spans,
                                                   actual_data_converter=lambda l: [t[0] for t in l])


def test_safe_index():
    actual = _safe_index('hello world', 'world', 1)
    assert actual == 6


def test_safe_index_not_found():
    try:
        _safe_index('hello world', 'world', 7)
        raise AssertionError('Should raise ValueError before this line')
    except ValueError as e:
        assert 'start' in str(e)

# def test_bad_cases():
#    lexnlp_tests.test_extraction_func_on_test_data(get_addresses)
