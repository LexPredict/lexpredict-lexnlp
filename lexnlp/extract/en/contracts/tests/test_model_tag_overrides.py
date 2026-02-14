import pytest

from lexnlp.extract.en.contracts.predictors import (
    ProbabilityPredictorContractType,
    ProbabilityPredictorIsContract,
)
from lexnlp.extract.en.contracts import runtime_model
from lexnlp.ml import catalog as ml_catalog
from lexnlp.ml.predictor import ProbabilityPredictor


def test_is_contract_default_pipeline_tag_no_env(monkeypatch):
    monkeypatch.delenv("LEXNLP_IS_CONTRACT_MODEL_TAG", raising=False)
    assert ProbabilityPredictorIsContract.get_default_pipeline_tag() == "pipeline/is-contract/0.2"


def test_is_contract_default_pipeline_tag_with_env(monkeypatch):
    monkeypatch.setenv("LEXNLP_IS_CONTRACT_MODEL_TAG", "pipeline/is-contract/0.2")
    assert ProbabilityPredictorIsContract.get_default_pipeline_tag() == "pipeline/is-contract/0.2"


def test_is_contract_default_pipeline_falls_back_to_legacy(monkeypatch, tmp_path):
    sentinel_pipeline = object()

    def raise_default_load_error(cls):
        raise FileNotFoundError("missing default model")

    monkeypatch.delenv("LEXNLP_IS_CONTRACT_MODEL_TAG", raising=False)
    monkeypatch.setattr(
        ProbabilityPredictor,
        "get_default_pipeline",
        classmethod(raise_default_load_error),
    )

    legacy_path = tmp_path / "pipeline_is_contract_classifier.cloudpickle"
    legacy_path.write_bytes(b"not a real pickle")

    calls = {"catalog": 0, "load": 0}

    def get_path(tag: str):
        calls["catalog"] += 1
        assert tag == ProbabilityPredictorIsContract._LEGACY_FALLBACK_PIPELINE
        return legacy_path

    monkeypatch.setattr(ml_catalog, "get_path_from_catalog", get_path)

    import cloudpickle

    def fake_load(_file_obj):
        calls["load"] += 1
        return sentinel_pipeline

    monkeypatch.setattr(cloudpickle, "load", fake_load)

    result = ProbabilityPredictorIsContract.get_default_pipeline()
    assert result is sentinel_pipeline
    assert calls == {"catalog": 1, "load": 1}


def test_is_contract_env_override_failure_does_not_trigger_legacy_fallback(monkeypatch):
    def raise_override_load_error(cls):
        raise ValueError("missing override model")

    monkeypatch.setenv("LEXNLP_IS_CONTRACT_MODEL_TAG", "pipeline/is-contract/custom")
    monkeypatch.setattr(
        ProbabilityPredictor,
        "get_default_pipeline",
        classmethod(raise_override_load_error),
    )

    with pytest.raises(ValueError, match="missing override model"):
        ProbabilityPredictorIsContract.get_default_pipeline()


def test_contract_type_default_pipeline_tag_no_env(monkeypatch):
    monkeypatch.delenv("LEXNLP_CONTRACT_TYPE_MODEL_TAG", raising=False)
    assert ProbabilityPredictorContractType.get_default_pipeline_tag() == "pipeline/contract-type/0.1"


def test_contract_type_default_pipeline_tag_with_env(monkeypatch):
    monkeypatch.setenv("LEXNLP_CONTRACT_TYPE_MODEL_TAG", "pipeline/contract-type/0.2")
    assert ProbabilityPredictorContractType.get_default_pipeline_tag() == "pipeline/contract-type/0.2"


def test_contract_type_default_pipeline_falls_back_to_runtime_model(monkeypatch):
    sentinel_pipeline = object()

    def raise_legacy_load_error(cls):
        raise TypeError("legacy model pickle is incompatible")

    monkeypatch.delenv("LEXNLP_CONTRACT_TYPE_MODEL_TAG", raising=False)
    monkeypatch.setattr(
        ProbabilityPredictor,
        "get_default_pipeline",
        classmethod(raise_legacy_load_error),
    )

    calls = {"ensure": 0, "load": 0}

    def ensure_runtime(*, target_tag):
        calls["ensure"] += 1
        assert target_tag == ProbabilityPredictorContractType._RUNTIME_FALLBACK_PIPELINE

    def load_fallback(tag: str):
        calls["load"] += 1
        assert tag == ProbabilityPredictorContractType._RUNTIME_FALLBACK_PIPELINE
        return sentinel_pipeline

    monkeypatch.setattr(runtime_model, "ensure_runtime_contract_type_model", ensure_runtime)
    monkeypatch.setattr(runtime_model, "load_pipeline_for_tag", load_fallback)

    result = ProbabilityPredictorContractType.get_default_pipeline()
    assert result is sentinel_pipeline
    assert calls == {"ensure": 1, "load": 1}


def test_contract_type_env_override_failure_does_not_trigger_runtime_fallback(monkeypatch):
    def raise_override_load_error(cls):
        raise ValueError("missing override model")

    monkeypatch.setenv("LEXNLP_CONTRACT_TYPE_MODEL_TAG", "pipeline/contract-type/custom")
    monkeypatch.setattr(
        ProbabilityPredictor,
        "get_default_pipeline",
        classmethod(raise_override_load_error),
    )

    called = {"ensure": 0}

    def ensure_runtime(*, target_tag):
        called["ensure"] += 1

    monkeypatch.setattr(runtime_model, "ensure_runtime_contract_type_model", ensure_runtime)

    with pytest.raises(ValueError, match="missing override model"):
        ProbabilityPredictorContractType.get_default_pipeline()
    assert called["ensure"] == 0
