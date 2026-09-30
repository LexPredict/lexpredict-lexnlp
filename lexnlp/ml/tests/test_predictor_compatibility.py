import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler

from lexnlp.extract.en.contracts.predictors import ProbabilityPredictorIsContract


def fitted_pipeline() -> Pipeline:
    pipeline = Pipeline(
        [
            ("scale", MinMaxScaler()),
            ("classify", GaussianNB()),
        ]
    )
    pipeline.fit(
        np.array([[0.0], [1.0], [2.0], [3.0]]),
        np.array([False, False, True, True]),
    )
    return pipeline


def test_user_supplied_legacy_pipeline_exposes_repair_report():
    pipeline = fitted_pipeline()
    scaler = pipeline.named_steps["scale"]
    classifier = pipeline.named_steps["classify"]
    del scaler.clip
    classifier.sigma_ = classifier.var_
    del classifier.var_

    predictor = ProbabilityPredictorIsContract(pipeline=pipeline)

    assert predictor.compatibility_report is not None
    assert predictor.compatibility_report.estimator_attribute_upgrades == 3
    assert scaler.clip is False
    assert classifier.var_ is classifier.sigma_
    assert classifier.variance_ is classifier.var_


def test_catalog_pipeline_does_not_claim_an_unobserved_report(monkeypatch):
    pipeline = fitted_pipeline()
    monkeypatch.setattr(
        ProbabilityPredictorIsContract,
        "get_default_pipeline",
        classmethod(lambda cls: pipeline),
    )

    predictor = ProbabilityPredictorIsContract()

    assert predictor.compatibility_report is None
