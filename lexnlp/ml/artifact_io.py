"""Crash-safe helpers for writing persisted model artifacts."""

from __future__ import annotations

import os
import pickle
import stat
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


@contextmanager
def atomic_output_path(destination: Path) -> Iterator[Path]:
    """Yield a sibling temporary path and atomically publish it on success."""
    destination = Path(destination)
    if destination.is_symlink():
        raise ValueError(
            f"Refusing to replace a model artifact symlink: {destination}"
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination_mode = (
        stat.S_IMODE(destination.stat().st_mode)
        if destination.exists()
        else 0o644
    )
    file_descriptor, temporary_name = tempfile.mkstemp(
        dir=destination.parent,
        prefix=f".{destination.name}.",
        suffix=".tmp",
    )
    os.close(file_descriptor)
    temporary_path = Path(temporary_name)

    try:
        yield temporary_path
        if not temporary_path.is_file() or temporary_path.stat().st_size == 0:
            raise RuntimeError(
                f"Refusing to publish an empty model artifact: {temporary_path}"
            )
        os.chmod(temporary_path, destination_mode)
        with temporary_path.open("rb") as temporary_file:
            os.fsync(temporary_file.fileno())
        temporary_path.replace(destination)
        try:
            directory_descriptor = os.open(destination.parent, os.O_RDONLY)
        except OSError:
            # Directory handles are not available on every supported platform.
            pass
        else:
            try:
                os.fsync(directory_descriptor)
            finally:
                os.close(directory_descriptor)
    finally:
        temporary_path.unlink(missing_ok=True)


def atomic_pickle_dump(
    value: object,
    destination: Path,
    *,
    protocol: int | None = None,
) -> None:
    """Serialize a pickle without exposing a partially written destination."""
    with atomic_output_path(destination) as temporary_path:
        with temporary_path.open("wb") as output_file:
            if protocol is None:
                pickle.dump(value, output_file)
            else:
                pickle.dump(value, output_file, protocol=protocol)
            output_file.flush()
            os.fsync(output_file.fileno())
