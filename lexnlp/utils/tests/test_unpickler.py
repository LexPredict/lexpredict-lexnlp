import subprocess
import sys
import pickle
from io import BytesIO
from pathlib import Path
from textwrap import dedent

import numpy as np
from joblib import numpy_pickle
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import MinMaxScaler
from sklearn.tree import DecisionTreeClassifier

from lexnlp.utils.unpickler import (
    CompatibilityReport,
    load_joblib_model,
    renamed_load,
)


def test_importing_lexnlp_does_not_patch_joblib_unpickler():
    repository_root = Path(__file__).resolve().parents[3]
    code = dedent(
        """
        from joblib import numpy_pickle

        original_find_class = numpy_pickle.NumpyUnpickler.find_class
        import lexnlp

        if numpy_pickle.NumpyUnpickler.find_class is not original_find_class:
            raise SystemExit("LexNLP import replaced Joblib's global unpickler")
        """
    )

    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=repository_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr or completed.stdout


def test_legacy_sklearn_rename_is_local_to_lexnlp_load():
    original_find_class = numpy_pickle.NumpyUnpickler.find_class
    legacy_reference = b"csklearn.tree.tree\nDecisionTreeClassifier\n."

    loaded = renamed_load(BytesIO(legacy_reference))

    assert loaded is DecisionTreeClassifier
    assert numpy_pickle.NumpyUnpickler.find_class is original_find_class


def test_bundled_tree_model_load_is_local_and_prediction_compatible():
    original_find_class = numpy_pickle.NumpyUnpickler.find_class
    repository_root = Path(__file__).resolve().parents[3]
    model_path = repository_root / "lexnlp/nlp/en/segments/page_segmenter.pickle"

    model = load_joblib_model(model_path)
    features = np.vstack(
        [
            np.zeros(model.n_features_),
            np.ones(model.n_features_),
            np.arange(model.n_features_),
        ]
    )

    assert model.predict(features).tolist() == [0, 1, 1]
    assert model.predict_proba(features).tolist() == [
        [1.0, 0.0],
        [0.0, 1.0],
        [0.0, 1.0],
    ]
    assert numpy_pickle.NumpyUnpickler.find_class is original_find_class


def test_bundled_forest_model_load_preserves_probabilities():
    repository_root = Path(__file__).resolve().parents[3]
    model_path = repository_root / "lexnlp/nlp/en/segments/title_locator.pickle"

    model = load_joblib_model(model_path)
    features = np.vstack(
        [
            np.zeros(model.n_features_),
            np.ones(model.n_features_),
            np.arange(model.n_features_),
        ]
    )

    assert model.predict(features).tolist() == [0.0, 0.0, 0.0]
    assert model.predict_proba(features).tolist() == [
        [1.0, 0.0],
        [0.76, 0.24],
        [0.92, 0.08],
    ]


def test_compatibility_walks_estimators_nested_in_object_array():
    scaler = MinMaxScaler()
    del scaler.clip
    classifier = GaussianNB()
    classifier.sigma_ = np.array([1.0, 2.0])

    nested = np.empty(2, dtype=object)
    nested[:] = [scaler, {"classifier": classifier}]
    report = CompatibilityReport()

    loaded = renamed_load(
        BytesIO(pickle.dumps({"nested": nested})),
        report=report,
    )

    loaded_scaler = loaded["nested"][0]
    loaded_classifier = loaded["nested"][1]["classifier"]
    assert loaded_scaler.clip is False
    assert loaded_classifier.var_ is loaded_classifier.sigma_
    assert loaded_classifier.variance_ is loaded_classifier.var_
    assert report.estimator_attribute_upgrades == 3
