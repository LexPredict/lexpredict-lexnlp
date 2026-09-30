from pandas import Series

from lexnlp.extract.en.contracts.contract_type_detector import ContractTypeDetector
from lexnlp.extract.en.contracts.predictors import ProbabilityPredictorContractType


def contract_type_predictions() -> Series:
    return Series(
        [0.9, 0.1],
        index=["EMPLOYMENT AGREEMENT", "SERVICES AGREEMENT"],
    )


def test_probability_predictor_uses_series_positions_with_string_labels():
    result = ProbabilityPredictorContractType.infer_classification(
        contract_type_predictions(),
    )

    assert result == "EMPLOYMENT AGREEMENT"


def test_legacy_detector_uses_series_positions_with_string_labels():
    result = ContractTypeDetector.detect_contract_type(
        contract_type_predictions(),
    )

    assert result == "EMPLOYMENT AGREEMENT"
