import hashlib
import json
import stat
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import reexport_bundled_sklearn_models
from scripts._artifact_transaction import publish_staged_files


def _prepare_bundled_reexport(monkeypatch, tmp_path: Path) -> SimpleNamespace:
    first = tmp_path / "first.pickle"
    second = tmp_path / "second.pickle"
    metadata = tmp_path / "reexport-metadata.json"

    first.write_bytes(b"previous-first")
    first.chmod(0o640)
    second.write_bytes(b"previous-second")
    second.chmod(0o604)
    metadata.write_bytes(b"previous-metadata")
    metadata.chmod(0o600)

    model_paths = (first, second)
    monkeypatch.setattr(
        reexport_bundled_sklearn_models,
        "assert_model_artifact_runtime",
        dict,
    )
    monkeypatch.setattr(
        reexport_bundled_sklearn_models,
        "load_model",
        lambda path, report=None: path.name,
    )

    def fake_dump(model, path, *, compress):
        Path(path).write_bytes(f"candidate:{model}:{compress}".encode())
        return [str(path)]

    monkeypatch.setattr(
        reexport_bundled_sklearn_models.joblib,
        "dump",
        fake_dump,
    )
    monkeypatch.setattr(
        reexport_bundled_sklearn_models,
        "load_diagnostics",
        lambda path: (0, 0, 0, 0),
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
        reexport_bundled_sklearn_models,
        "artifact_metadata",
        fake_artifact_metadata,
    )

    args = [
        "--paths",
        *(str(path) for path in model_paths),
        "--metadata-output",
        str(metadata),
    ]
    return SimpleNamespace(
        args=args,
        model_paths=model_paths,
        metadata=metadata,
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


def test_candidate_diagnostics_rejection_preserves_all_outputs(
    monkeypatch,
    tmp_path: Path,
):
    prepared = _prepare_bundled_reexport(monkeypatch, tmp_path)
    before = _snapshot(*prepared.model_paths, prepared.metadata)
    original_paths = set(prepared.model_paths)

    def reject_second_candidate(path: Path):
        if path not in original_paths and path.name == "second.pickle":
            return (1, 0, 0, 0)
        return (0, 0, 0, 0)

    monkeypatch.setattr(
        reexport_bundled_sklearn_models,
        "load_diagnostics",
        reject_second_candidate,
    )

    assert reexport_bundled_sklearn_models.main(prepared.args) == 1
    _assert_snapshot(before)


def test_candidate_post_load_exception_preserves_all_outputs(
    monkeypatch,
    tmp_path: Path,
):
    prepared = _prepare_bundled_reexport(monkeypatch, tmp_path)
    before = _snapshot(*prepared.model_paths, prepared.metadata)
    original_paths = set(prepared.model_paths)

    def fail_second_candidate(path: Path):
        if path not in original_paths and path.name == "second.pickle":
            raise ValueError("candidate post-load failed")
        return (0, 0, 0, 0)

    monkeypatch.setattr(
        reexport_bundled_sklearn_models,
        "load_diagnostics",
        fail_second_candidate,
    )

    with pytest.raises(ValueError, match="post-load failed"):
        reexport_bundled_sklearn_models.main(prepared.args)
    _assert_snapshot(before)


def test_success_publishes_all_models_and_metadata_preserving_modes(
    monkeypatch,
    tmp_path: Path,
):
    prepared = _prepare_bundled_reexport(monkeypatch, tmp_path)
    modes = {
        path: stat.S_IMODE(path.stat().st_mode)
        for path in (*prepared.model_paths, prepared.metadata)
    }

    assert reexport_bundled_sklearn_models.main(prepared.args) == 0

    for path in prepared.model_paths:
        expected = f"candidate:{path.name}:3".encode()
        assert path.read_bytes() == expected
        assert stat.S_IMODE(path.stat().st_mode) == modes[path]

    metadata = json.loads(prepared.metadata.read_text(encoding="utf-8"))
    assert [item["path"] for item in metadata["artifacts"]] == [
        path.as_posix()
        for path in prepared.model_paths
    ]
    assert metadata["artifacts"][0]["artifact_sha256"] == hashlib.sha256(
        prepared.model_paths[0].read_bytes()
    ).hexdigest()
    assert stat.S_IMODE(prepared.metadata.stat().st_mode) == modes[
        prepared.metadata
    ]


def test_mid_publish_exception_rolls_back_models_and_metadata_with_modes(
    monkeypatch,
    tmp_path: Path,
):
    prepared = _prepare_bundled_reexport(monkeypatch, tmp_path)
    before = _snapshot(*prepared.model_paths, prepared.metadata)
    real_replace = Path.replace

    def fail_metadata_commit(self: Path, target: Path):
        target = Path(target)
        is_metadata_commit = (
            target.resolve(strict=False)
            == prepared.metadata.resolve(strict=False)
            and self.suffix == ".tmp"
        )
        if is_metadata_commit:
            raise OSError("simulated metadata publication failure")
        return real_replace(self, target)

    monkeypatch.setattr(Path, "replace", fail_metadata_commit)

    with pytest.raises(OSError, match="simulated metadata"):
        reexport_bundled_sklearn_models.main(prepared.args)

    _assert_snapshot(before)
    assert not list(tmp_path.glob(".*.rollback"))
    assert not list(tmp_path.glob(".*.tmp"))


def test_failed_rollback_retains_recoverable_backup(
    monkeypatch,
    tmp_path: Path,
):
    first = tmp_path / "first.pickle"
    second = tmp_path / "second.pickle"
    staged_first = tmp_path / "staged-first.pickle"
    staged_second = tmp_path / "staged-second.pickle"
    first.write_bytes(b"previous-first")
    second.write_bytes(b"previous-second")
    staged_first.write_bytes(b"candidate-first")
    staged_second.write_bytes(b"candidate-second")
    real_replace = Path.replace

    def fail_commit_and_first_restore(self: Path, target: Path):
        target = Path(target)
        if self.suffix == ".tmp" and target == second:
            raise OSError("simulated commit failure")
        if self.suffix == ".rollback" and target == first:
            raise OSError("simulated rollback failure")
        return real_replace(self, target)

    monkeypatch.setattr(Path, "replace", fail_commit_and_first_restore)

    with pytest.raises(RuntimeError, match="backup retained at"):
        publish_staged_files(
            (
                (first, staged_first),
                (second, staged_second),
            )
        )

    assert second.read_bytes() == b"previous-second"
    retained = list(tmp_path.glob(".first.pickle.*.rollback"))
    assert len(retained) == 1
    assert retained[0].read_bytes() == b"previous-first"


def test_check_current_still_publishes_requested_metadata(
    monkeypatch,
    tmp_path: Path,
):
    prepared = _prepare_bundled_reexport(monkeypatch, tmp_path)
    model_before = _snapshot(*prepared.model_paths)
    metadata_mode = stat.S_IMODE(prepared.metadata.stat().st_mode)
    args = [*prepared.args, "--check-current"]

    assert reexport_bundled_sklearn_models.main(args) == 0

    _assert_snapshot(model_before)
    metadata = json.loads(prepared.metadata.read_text(encoding="utf-8"))
    assert len(metadata["artifacts"]) == 2
    assert stat.S_IMODE(prepared.metadata.stat().st_mode) == metadata_mode


def test_metadata_output_cannot_alias_a_model(
    monkeypatch,
    tmp_path: Path,
):
    prepared = _prepare_bundled_reexport(monkeypatch, tmp_path)
    before = _snapshot(*prepared.model_paths)
    args = [
        "--paths",
        *(str(path) for path in prepared.model_paths),
        "--metadata-output",
        str(prepared.model_paths[0].parent / "." / prepared.model_paths[0].name),
    ]

    with pytest.raises(ValueError, match="Metadata output must differ"):
        reexport_bundled_sklearn_models.main(args)
    _assert_snapshot(before)
