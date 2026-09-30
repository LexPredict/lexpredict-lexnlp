from pathlib import Path

import pytest

from lexnlp.ml.artifact_abi import (
    MODEL_ARTIFACT_RUNTIME,
    artifact_metadata,
    assert_model_artifact_runtime,
)


def test_assert_model_artifact_runtime_accepts_committed_versions():
    actual = {**MODEL_ARTIFACT_RUNTIME, "lexnlp": "2.3.0"}
    assert_model_artifact_runtime(actual)


def test_assert_model_artifact_runtime_reports_mismatch():
    actual = {**MODEL_ARTIFACT_RUNTIME, "numpy": "2.0.0"}
    with pytest.raises(RuntimeError, match=r"numpy='2\.0\.0'"):
        assert_model_artifact_runtime(actual)


def test_artifact_metadata_includes_hash_and_runtime(tmp_path: Path):
    artifact = tmp_path / "model.pickle"
    artifact.write_bytes(b"lexnlp-model")

    metadata = artifact_metadata(artifact)

    assert metadata["artifact_path"] == str(artifact)
    assert metadata["artifact_sha256"] == (
        "6321111ff4e6f6378d1610b08ef3b72951be4698cc7e11d84fe55305376013b2"
    )
    assert metadata["artifact_size_bytes"] == 12
    assert set(metadata["runtime"]) >= {
        "python",
        "scikit_learn",
        "numpy",
        "joblib",
        "lexnlp",
    }
