#!/usr/bin/env python3
"""Validate built distribution contents."""

from __future__ import annotations

import sys
import tarfile
import zipfile
from pathlib import Path
from typing import Iterable, List

BANNED_SUBSTRINGS = (
    "libs/stanford_nlp/",
    "scripts/__pycache__/",
)

BANNED_BASENAMES = (
    "Pipfile",
    "Pipfile.lock",
    "python-requirements.txt",
    "python-requirements-dev.txt",
    "python-requirements-full.txt",
)

BANNED_SUFFIXES = (
    ".pyc",
    ".pyo",
)


def iter_tar_names(path: Path) -> Iterable[str]:
    with tarfile.open(path, "r:*") as archive:
        for member in archive.getmembers():
            if member.isfile():
                yield member.name


def iter_zip_names(path: Path) -> Iterable[str]:
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if not name.endswith("/"):
                yield name


def find_violations(names: Iterable[str]) -> List[str]:
    violations: List[str] = []
    for name in names:
        normalized = name.replace("\\", "/")
        if any(token in normalized for token in BANNED_SUBSTRINGS):
            violations.append(normalized)
            continue
        if normalized.rsplit("/", 1)[-1] in BANNED_BASENAMES:
            violations.append(normalized)
            continue
        if normalized.endswith(BANNED_SUFFIXES):
            violations.append(normalized)
    return violations


def main(argv: list[str]) -> int:
    dist_dir = Path(argv[0]) if argv else Path("dist")
    if not dist_dir.exists():
        print(f"dist-check: missing dist directory: {dist_dir}", file=sys.stderr)
        return 1

    artifacts = sorted(
        [*dist_dir.glob("*.whl"), *dist_dir.glob("*.tar.gz")]
    )
    if not artifacts:
        print(f"dist-check: no build artifacts found under {dist_dir}", file=sys.stderr)
        return 1

    failures: List[str] = []
    for artifact in artifacts:
        if artifact.suffix == ".whl":
            names = iter_zip_names(artifact)
        else:
            names = iter_tar_names(artifact)
        violations = find_violations(names)
        for violation in violations:
            failures.append(f"{artifact.name}: {violation}")

    if failures:
        print("dist-check: forbidden files found in artifacts", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print("dist-check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
