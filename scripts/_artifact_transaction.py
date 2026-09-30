"""Transactional publication helpers for model re-export scripts."""

from __future__ import annotations

import os
import shutil
import stat
from collections.abc import Sequence
from pathlib import Path
from uuid import uuid4

from lexnlp.ml.artifact_io import atomic_output_path

Publication = tuple[Path, Path]


def _copy_backup(source: Path, destination: Path) -> None:
    """Copy an existing target to an exclusively-created rollback file."""
    source_mode = stat.S_IMODE(source.stat().st_mode)
    with (
        source.open("rb") as source_file,
        destination.open("xb") as backup_file,
    ):
        shutil.copyfileobj(source_file, backup_file)
        backup_file.flush()
        os.fsync(backup_file.fileno())
    os.chmod(destination, source_mode)


def _backup_path(destination: Path) -> Path:
    """Create a same-directory hard-link backup, falling back to a byte copy."""
    while True:
        backup = destination.parent / (
            f".{destination.name}.{uuid4().hex}.rollback"
        )
        try:
            os.link(destination, backup, follow_symlinks=False)
        except FileExistsError:
            continue
        except OSError:
            try:
                _copy_backup(destination, backup)
            except BaseException:
                backup.unlink(missing_ok=True)
                raise
        return backup


def _fsync_directory(path: Path) -> None:
    try:
        directory_descriptor = os.open(path, os.O_RDONLY)
    except OSError:
        # Directory handles are not available on every supported platform.
        return
    try:
        os.fsync(directory_descriptor)
    finally:
        os.close(directory_descriptor)


def publish_staged_files(publications: Sequence[Publication]) -> None:
    """Publish staged files as one rollback-capable transaction.

    Each staged file is copied through ``atomic_output_path`` so the destination
    keeps its prior mode and readers never observe partial bytes. Existing
    destinations are backed up before the first replacement. If any later
    publication fails, every attempted destination is restored to its exact
    pre-transaction state.
    """
    normalized = [
        (Path(destination), Path(staged))
        for destination, staged in publications
    ]
    if not normalized:
        return

    destinations_by_identity: dict[Path, Path] = {}
    for destination, _ in normalized:
        identity = destination.resolve(strict=False)
        prior = destinations_by_identity.get(identity)
        if prior is not None:
            raise ValueError(
                "Duplicate artifact publication destination: "
                f"{prior} and {destination}"
            )
        destinations_by_identity[identity] = destination

    unique_destinations = list(destinations_by_identity.values())
    for destination in unique_destinations:
        if destination.is_symlink():
            raise ValueError(
                f"Refusing to replace a model artifact symlink: {destination}"
            )

    backups: dict[Path, Path | None] = {}
    attempted: list[Path] = []
    attempted_set: set[Path] = set()
    retained_backups: set[Path] = set()
    try:
        for destination in unique_destinations:
            backups[destination] = (
                _backup_path(destination)
                if destination.exists()
                else None
            )

        for destination, staged in normalized:
            with atomic_output_path(destination) as temporary_path:
                shutil.copyfile(staged, temporary_path)
                if destination not in attempted_set:
                    attempted.append(destination)
                    attempted_set.add(destination)
    except BaseException as publication_error:
        rollback_errors: list[str] = []
        for destination in reversed(attempted):
            backup = backups.get(destination)
            try:
                if backup is None:
                    destination.unlink(missing_ok=True)
                else:
                    backup.replace(destination)
                _fsync_directory(destination.parent)
            except OSError as rollback_error:
                recovery_detail = ""
                if backup is not None and backup.exists():
                    retained_backups.add(backup)
                    recovery_detail = f"; backup retained at {backup}"
                rollback_errors.append(
                    f"{destination}: {rollback_error}{recovery_detail}"
                )

        if rollback_errors:
            details = "; ".join(rollback_errors)
            raise RuntimeError(
                "Artifact publication failed and rollback was incomplete: "
                f"{details}"
            ) from publication_error
        raise
    finally:
        for backup in backups.values():
            if backup is not None and backup not in retained_backups:
                backup.unlink(missing_ok=True)
