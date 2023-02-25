__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from lexnlp.extract.en.contracts.predictors import ProbabilityPredictorIsContract
from lexnlp.tests import lexnlp_tests


def actual_data_converter(val):
    return [str(val)]


def test_is_contract():

    probability_predictor_is_contract: ProbabilityPredictorIsContract = \
        ProbabilityPredictorIsContract(pipeline=ProbabilityPredictorIsContract.get_default_pipeline())

    lexnlp_tests.test_extraction_func_on_test_data(
        probability_predictor_is_contract.is_contract,
        actual_data_converter=actual_data_converter,
        min_probability=0.3)

# def test_bad_cases():
#    lexnlp_tests.test_extraction_func_on_test_data(get_addresses)
