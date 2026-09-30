import hashlib
import json
import os
import pickle
import stat
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import reexport_contract_model


def _prepare_contract_reexport(monkeypatch, tmp_path: Path) -> SimpleNamespace:
    from lexnlp.extract.en.contracts import predictors
    from lexnlp.ml import artifact_abi, catalog
    from lexnlp.utils import unpickler

    source_tag = "pipeline/is-contract/source"
    target_tag = "pipeline/is-contract/target"
    pipeline = {"classes": [False, True], "version": "candidate"}

    source_path = tmp_path / "source" / "model.pickle"
    source_path.parent.mkdir()
    source_path.write_bytes(
        pickle.dumps(pipeline, protocol=pickle.HIGHEST_PROTOCOL)
    )

    catalog_root = tmp_path / "catalog"
    destination_path = catalog_root / target_tag / source_path.name
    destination_path.parent.mkdir(parents=True)
    destination_path.write_bytes(b"previous-good-model")
    destination_path.chmod(0o640)

    metadata_path = tmp_path / "reports" / "contract.metadata.json"
    metadata_path.parent.mkdir()
    metadata_path.write_bytes(b"previous-good-metadata")
    metadata_path.chmod(0o600)

    monkeypatch.setattr(catalog, "CATALOG", catalog_root)
    monkeypatch.setattr(
        reexport_contract_model,
        "ensure_tag_downloaded",
        lambda tag: source_path,
    )
    monkeypatch.setattr(
        artifact_abi,
        "assert_model_artifact_runtime",
        dict,
    )

    def fake_artifact_metadata(path: Path):
        payload = path.read_bytes()
        return {
            "artifact_path": str(path),
            "artifact_sha256": hashlib.sha256(payload).hexdigest(),
            "artifact_size_bytes": len(payload),
            "runtime": {"python": "test"},
        }

    monkeypatch.setattr(
        artifact_abi,
        "artifact_metadata",
        fake_artifact_metadata,
    )
    monkeypatch.setattr(unpickler, "load_sklearn_model", pickle.load)

    class FakePredictor:
        def __init__(self, *, pipeline):
            self.pipeline = pipeline

    monkeypatch.setattr(
        predictors,
        "ProbabilityPredictorIsContract",
        FakePredictor,
    )
    monkeypatch.setattr(
        reexport_contract_model,
        "get_legacy_warning_messages",
        lambda path: [],
    )
    monkeypatch.setattr(
        reexport_contract_model,
        "run_quality_gate",
        lambda **kwargs: None,
    )

    args = [
        "--source-tag",
        source_tag,
        "--target-tag",
        target_tag,
        "--force",
        "--output-metadata-json",
        str(metadata_path),
    ]
    return SimpleNamespace(
        args=args,
        source_tag=source_tag,
        target_tag=target_tag,
        pipeline=pipeline,
        source_path=source_path,
        destination_path=destination_path,
        metadata_path=metadata_path,
    )


def _snapshot(*paths: Path) -> dict[Path, tuple[bytes, int]]:
    return {
        path: (path.read_bytes(), stat.S_IMODE(path.stat().st_mode))
        for path in paths
    }


def _assert_snapshot(snapshot: dict[Path, tuple[bytes, int]]) -> None:
    for path, (expected_bytes, expected_mode) in snapshot.items():
        assert path.read_bytes() == expected_bytes
        assert stat.S_IMODE(path.stat().st_mode) == expected_mode


def test_warning_rejection_preserves_existing_model_and_metadata(
    monkeypatch,
    tmp_path: Path,
):
    prepared = _prepare_contract_reexport(monkeypatch, tmp_path)
    before = _snapshot(prepared.destination_path, prepared.metadata_path)

    monkeypatch.setattr(
        reexport_contract_model,
        "get_legacy_warning_messages",
        lambda path: [] if path == prepared.source_path else ["legacy warning"],
    )
    monkeypatch.setattr(
        reexport_contract_model,
        "run_quality_gate",
        lambda **kwargs: pytest.fail("quality gate must not run"),
    )

    assert reexport_contract_model.main(prepared.args) == 1
    _assert_snapshot(before)


def test_post_load_validation_failure_preserves_existing_outputs(
    monkeypatch,
    tmp_path: Path,
):
    prepared = _prepare_contract_reexport(monkeypatch, tmp_path)
    before = _snapshot(prepared.destination_path, prepared.metadata_path)

    from lexnlp.extract.en.contracts import predictors

    validations = 0

    def validate_candidate(*, pipeline):
        nonlocal validations
        validations += 1
        if validations == 2:
            raise ValueError("candidate failed post-load validation")

    monkeypatch.setattr(
        predictors,
        "ProbabilityPredictorIsContract",
        validate_candidate,
    )

    with pytest.raises(ValueError, match="post-load validation"):
        reexport_contract_model.main(prepared.args)
    _assert_snapshot(before)


def test_quality_gate_failure_preserves_existing_outputs(
    monkeypatch,
    tmp_path: Path,
):
    prepared = _prepare_contract_reexport(monkeypatch, tmp_path)
    before = _snapshot(prepared.destination_path, prepared.metadata_path)

    def reject_quality(**kwargs):
        assert prepared.destination_path.read_bytes() == before[
            prepared.destination_path
        ][0]
        raise subprocess.CalledProcessError(1, ["model_quality_gate.py"])

    monkeypatch.setattr(
        reexport_contract_model,
        "run_quality_gate",
        reject_quality,
    )

    with pytest.raises(subprocess.CalledProcessError):
        reexport_contract_model.main(prepared.args)
    _assert_snapshot(before)


def test_success_gates_staged_candidate_then_publishes_model_and_metadata(
    monkeypatch,
    tmp_path: Path,
):
    prepared = _prepare_contract_reexport(monkeypatch, tmp_path)
    expected_model = pickle.dumps(
        prepared.pipeline,
        protocol=pickle.HIGHEST_PROTOCOL,
    )
    destination_mode = stat.S_IMODE(prepared.destination_path.stat().st_mode)
    metadata_mode = stat.S_IMODE(prepared.metadata_path.stat().st_mode)

    prior_nltk_data = tmp_path / "prior-nltk-data"
    sentinel_resource = prior_nltk_data / "sentinel-resource"
    sentinel_resource.mkdir(parents=True)
    monkeypatch.setenv("NLTK_DATA", str(prior_nltk_data))
    gate_calls = []

    def accept_quality(**kwargs):
        assert prepared.destination_path.read_bytes() == b"previous-good-model"
        nltk_data_paths = os.environ["NLTK_DATA"].split(os.pathsep)
        isolated_root = Path(nltk_data_paths[0])
        assert isolated_root.is_dir()
        assert nltk_data_paths[1:] == [str(prior_nltk_data)]
        probe = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import sys\n"
                    "import nltk.data\n"
                    "from lexnlp.ml.catalog import get_path_from_catalog\n"
                    "print(get_path_from_catalog(sys.argv[1]))\n"
                    "print(nltk.data.find(sys.argv[2]))\n"
                ),
                prepared.target_tag,
                sentinel_resource.name,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        candidate_raw, sentinel_raw = probe.stdout.splitlines()
        candidate = Path(candidate_raw)
        assert candidate.read_bytes() == expected_model
        assert Path(sentinel_raw) == sentinel_resource
        gate_calls.append(kwargs)

    monkeypatch.setattr(
        reexport_contract_model,
        "run_quality_gate",
        accept_quality,
    )

    assert reexport_contract_model.main(prepared.args) == 0

    assert len(gate_calls) == 1
    assert os.environ["NLTK_DATA"] == str(prior_nltk_data)
    assert prepared.destination_path.read_bytes() == expected_model
    assert stat.S_IMODE(prepared.destination_path.stat().st_mode) == destination_mode
    metadata = json.loads(prepared.metadata_path.read_text(encoding="utf-8"))
    assert metadata["artifact_path"] == str(prepared.destination_path)
    assert metadata["artifact_sha256"] == hashlib.sha256(expected_model).hexdigest()
    assert stat.S_IMODE(prepared.metadata_path.stat().st_mode) == metadata_mode


@pytest.mark.parametrize("alias", ("source", "destination"))
def test_metadata_output_cannot_alias_a_model_path(
    monkeypatch,
    tmp_path: Path,
    alias: str,
):
    prepared = _prepare_contract_reexport(monkeypatch, tmp_path)
    before = _snapshot(prepared.source_path, prepared.destination_path)
    metadata_alias = (
        prepared.source_path
        if alias == "source"
        else prepared.destination_path
    )
    args = [
        *prepared.args[:-1],
        str(metadata_alias.parent / "." / metadata_alias.name),
    ]

    with pytest.raises(ValueError, match="Metadata output must differ"):
        reexport_contract_model.main(args)
    _assert_snapshot(before)
