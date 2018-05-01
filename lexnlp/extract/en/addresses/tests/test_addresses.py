from lexnlp.extract.en.addresses.addresses import get_addresses
from lexnlp.tests import lexnlp_tests

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.6"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def test_get_address():
    lexnlp_tests.test_extraction_func_on_test_data(get_addresses)

# def test_bad_cases():
#    lexnlp_tests.test_extraction_func_on_test_data(get_addresses)
