from lexnlp.extract.en.contracts.detector import is_contract
from lexnlp.tests import lexnlp_tests

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def actual_data_converter(val):
    return [str(val)]


def test_is_contract():
    lexnlp_tests.test_extraction_func_on_test_data(
        is_contract,
        actual_data_converter=actual_data_converter,
        min_probability=0.3)

# def test_bad_cases():
#    lexnlp_tests.test_extraction_func_on_test_data(get_addresses)
