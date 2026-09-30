"""Reproducible runtime metadata for persisted LexNLP model artifacts."""

from __future__ import annotations

import hashlib
import platform
from importlib.metadata import version
from pathlib import Path
from typing import Mapping

from lexnlp import __version__ as lexnlp_version


# Persist models with the oldest supported numerical ABI, then prove that the
# resulting artifacts also load with the latest locked dependency set.
MODEL_ARTIFACT_RUNTIME = {
    "python": "3.12.13",
    "joblib": "1.5.0",
    "numpy": "1.26.4",
    "pandas": "2.2.0",
    "scikit_learn": "1.7.2",
    "scipy": "1.13.0",
    "threadpoolctl": "3.6.0",
}

_DISTRIBUTIONS = {
    "joblib": "joblib",
    "numpy": "numpy",
    "pandas": "pandas",
    "scikit_learn": "scikit-learn",
    "scipy": "scipy",
    "threadpoolctl": "threadpoolctl",
}


def current_runtime_versions() -> dict[str, str]:
    """Return the versions needed to reproduce a serialized model."""
    return {
        "python": platform.python_version(),
        **{
            key: version(distribution)
            for key, distribution in _DISTRIBUTIONS.items()
        },
        "lexnlp": lexnlp_version,
    }


def assert_model_artifact_runtime(
    versions: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Fail unless a model is being built with the committed artifact ABI."""
    actual = dict(versions or current_runtime_versions())
    mismatches = {
        key: {"expected": expected, "actual": actual.get(key)}
        for key, expected in MODEL_ARTIFACT_RUNTIME.items()
        if actual.get(key) != expected
    }
    if mismatches:
        details = ", ".join(
            f"{key}={values['actual']!r} (expected {values['expected']!r})"
            for key, values in sorted(mismatches.items())
        )
        raise RuntimeError(
            "Model artifacts must be built with constraints/model-artifact-abi.txt: "
            f"{details}"
        )
    return actual


def sha256_file(path: Path) -> str:
    """Hash an artifact without loading the whole file into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as artifact:
        for chunk in iter(lambda: artifact.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_metadata(path: Path) -> dict[str, object]:
    """Return runtime and integrity metadata for a generated model."""
    return {
        "artifact_path": str(path),
        "artifact_sha256": sha256_file(path),
        "artifact_size_bytes": path.stat().st_size,
        "runtime": current_runtime_versions(),
    }
