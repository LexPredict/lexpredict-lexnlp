import os
import pickle
import stat
from pathlib import Path

import pytest

from lexnlp.ml.artifact_io import atomic_output_path, atomic_pickle_dump


def test_atomic_output_path_replaces_destination_on_success(tmp_path: Path):
    destination = tmp_path / "model.pickle"
    destination.write_bytes(b"old")

    with atomic_output_path(destination) as temporary_path:
        assert temporary_path.parent == destination.parent
        temporary_path.write_bytes(b"new")

    assert destination.read_bytes() == b"new"
    assert not list(tmp_path.glob(f".{destination.name}.*.tmp"))


def test_atomic_output_path_preserves_destination_on_failure(tmp_path: Path):
    destination = tmp_path / "model.pickle"
    destination.write_bytes(b"old")

    with pytest.raises(RuntimeError, match="interrupted"):
        with atomic_output_path(destination) as temporary_path:
            temporary_path.write_bytes(b"partial")
            raise RuntimeError("interrupted")

    assert destination.read_bytes() == b"old"
    assert not list(tmp_path.glob(f".{destination.name}.*.tmp"))


def test_atomic_pickle_dump_preserves_serialized_bytes(tmp_path: Path):
    destination = tmp_path / "model.pickle"
    value = {"model": [1, 2, 3]}
    expected = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)

    atomic_pickle_dump(value, destination, protocol=pickle.HIGHEST_PROTOCOL)

    assert destination.read_bytes() == expected


def test_atomic_output_path_preserves_existing_destination_mode(
    monkeypatch,
    tmp_path: Path,
):
    destination = tmp_path / "model.pickle"
    destination.write_bytes(b"old")
    destination.chmod(0o640)
    expected_mode = stat.S_IMODE(destination.stat().st_mode)
    observed_modes = []
    real_chmod = os.chmod

    def record_chmod(path, mode):
        observed_modes.append(mode)
        real_chmod(path, mode)

    monkeypatch.setattr(os, "chmod", record_chmod)

    with atomic_output_path(destination) as temporary_path:
        temporary_path.write_bytes(b"new")

    assert observed_modes == [expected_mode]
    if os.name == "posix":
        assert stat.S_IMODE(destination.stat().st_mode) == expected_mode


def test_atomic_output_path_uses_readable_default_mode(monkeypatch, tmp_path: Path):
    destination = tmp_path / "model.pickle"
    observed_modes = []
    real_chmod = os.chmod

    def record_chmod(path, mode):
        observed_modes.append(mode)
        real_chmod(path, mode)

    monkeypatch.setattr(os, "chmod", record_chmod)

    with atomic_output_path(destination) as temporary_path:
        temporary_path.write_bytes(b"new")

    assert observed_modes == [0o644]
    if os.name == "posix":
        assert stat.S_IMODE(destination.stat().st_mode) == 0o644


def test_atomic_output_path_refuses_destination_symlink(monkeypatch, tmp_path: Path):
    destination = tmp_path / "model.pickle"
    monkeypatch.setattr(
        Path,
        "is_symlink",
        lambda path: path == destination,
    )

    with pytest.raises(ValueError, match="symlink"):
        with atomic_output_path(destination):
            pass
