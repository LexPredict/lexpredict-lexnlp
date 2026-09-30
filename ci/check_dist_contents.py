#!/usr/bin/env python3
"""Validate source, wheel, sdist, and installed-package resource parity."""

from __future__ import annotations

import argparse
import importlib.util
import sys
import tarfile
import zipfile
from collections import Counter
from collections.abc import Iterable, Mapping
from pathlib import Path, PurePosixPath

BANNED_SUBSTRINGS = (
    "documentation/docs/build/",
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

BANNED_WHEEL_PREFIXES = (
    "ci/",
    "documentation/",
    "libs/",
    "notebooks/",
    "scripts/",
)

# These are the resource types loaded from the installed lexnlp package at
# runtime. Keeping this list central makes newly added resources (including the
# catalog release-asset manifest) part of the parity check automatically.
RUNTIME_RESOURCE_SUFFIXES = (
    ".csv",
    ".json",
    ".pickle",
    ".pickle.gzip",
    ".txt",
    ".xml",
)

# Guard against accidentally replacing the full language dictionaries with the
# tiny fallback lists embedded in Python modules.
MIN_NONEMPTY_LINE_COUNTS = {
    "lexnlp/extract/en/data/abbreviations.txt": 1_200,
    "lexnlp/extract/en/data/pronouns.txt": 90,
    "lexnlp/extract/de/data/abbreviations.txt": 340,
}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "dist_dir",
        nargs="?",
        type=Path,
        default=Path("dist"),
        help="directory containing wheel and sdist artifacts (default: dist)",
    )
    parser.add_argument(
        "--source-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root used as the resource-parity baseline",
    )
    parser.add_argument(
        "--installed",
        action="store_true",
        help="check the lexnlp package visible to this Python interpreter",
    )
    return parser.parse_args(argv)


def is_runtime_resource(name: str) -> bool:
    return name.endswith(RUNTIME_RESOURCE_SUFFIXES)


def normalise_package_name(name: str) -> str | None:
    """Return an archive member as a path rooted at ``lexnlp/``."""
    parts = PurePosixPath(name.replace("\\", "/")).parts
    try:
        package_index = parts.index("lexnlp")
    except ValueError:
        return None
    normalised = "/".join(parts[package_index:])
    return normalised if is_runtime_resource(normalised) else None


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


def read_tar_resources(path: Path) -> dict[str, bytes]:
    resources: dict[str, bytes] = {}
    with tarfile.open(path, "r:*") as archive:
        for member in archive.getmembers():
            if not member.isfile():
                continue
            name = normalise_package_name(member.name)
            if name is None:
                continue
            extracted = archive.extractfile(member)
            if extracted is None:
                raise ValueError(f"could not read {member.name} from {path}")
            resources[name] = extracted.read()
    return resources


def read_zip_resources(path: Path) -> dict[str, bytes]:
    resources: dict[str, bytes] = {}
    with zipfile.ZipFile(path) as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue
            name = normalise_package_name(member.filename)
            if name is not None:
                resources[name] = archive.read(member)
    return resources


def read_directory_resources(package_dir: Path) -> dict[str, bytes]:
    resources: dict[str, bytes] = {}
    for path in sorted(package_dir.rglob("*")):
        if not path.is_file():
            continue
        name = path.relative_to(package_dir.parent).as_posix()
        if is_runtime_resource(name):
            resources[name] = path.read_bytes()
    return resources


def source_resources(source_root: Path) -> dict[str, bytes]:
    package_dir = source_root.resolve() / "lexnlp"
    if not package_dir.is_dir():
        raise ValueError(f"missing source package directory: {package_dir}")
    resources = read_directory_resources(package_dir)
    if not resources:
        raise ValueError(f"no runtime resources found under {package_dir}")
    return resources


def installed_resources() -> tuple[Path, dict[str, bytes]]:
    spec = importlib.util.find_spec("lexnlp")
    if spec is None or not spec.submodule_search_locations:
        raise ValueError("lexnlp is not installed for this Python interpreter")
    package_dir = Path(next(iter(spec.submodule_search_locations))).resolve()
    return package_dir, read_directory_resources(package_dir)


def find_violations(names: Iterable[str]) -> list[str]:
    violations: list[str] = []
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


def find_duplicate_members(names: Iterable[str]) -> list[str]:
    """Return archive member paths that occur more than once."""
    counts = Counter(name.replace("\\", "/") for name in names)
    return sorted(name for name, count in counts.items() if count > 1)


def find_duplicate_resources(names: Iterable[str]) -> list[str]:
    """Return package resource paths represented by multiple archive members."""
    resources = [
        normalised
        for name in names
        if (normalised := normalise_package_name(name)) is not None
    ]
    counts = Counter(resources)
    return sorted(name for name, count in counts.items() if count > 1)


def nonempty_line_count(payload: bytes) -> int:
    return sum(1 for line in payload.decode("utf-8").splitlines() if line.strip())


def find_resource_failures(
    expected: Mapping[str, bytes],
    actual: Mapping[str, bytes],
    label: str,
) -> list[str]:
    failures: list[str] = []
    missing = sorted(set(expected) - set(actual))
    for name in missing:
        failures.append(f"{label}: missing runtime resource: {name}")

    unexpected = sorted(set(actual) - set(expected))
    for name in unexpected:
        failures.append(f"{label}: unexpected runtime resource: {name}")

    for name in sorted(set(expected) & set(actual)):
        if actual[name] != expected[name]:
            failures.append(f"{label}: resource differs from source: {name}")

    for name, minimum in MIN_NONEMPTY_LINE_COUNTS.items():
        payload = actual.get(name)
        if payload is None:
            continue
        count = nonempty_line_count(payload)
        if count < minimum:
            failures.append(
                f"{label}: {name} has {count} non-empty lines; expected at least {minimum}"
            )
    return failures


def validate_source_resources(resources: Mapping[str, bytes]) -> list[str]:
    failures: list[str] = []
    for name, minimum in MIN_NONEMPTY_LINE_COUNTS.items():
        payload = resources.get(name)
        if payload is None:
            failures.append(f"source: missing required language dictionary: {name}")
            continue
        count = nonempty_line_count(payload)
        if count < minimum:
            failures.append(
                f"source: {name} has {count} non-empty lines; expected at least {minimum}"
            )
    return failures


def validate_installed(source_root: Path) -> int:
    try:
        expected = source_resources(source_root)
        package_dir, actual = installed_resources()
    except (OSError, ValueError) as exc:
        print(f"dist-check: {exc}", file=sys.stderr)
        return 1

    failures = [
        *validate_source_resources(expected),
        *find_resource_failures(expected, actual, f"installed package at {package_dir}"),
    ]
    if failures:
        print("dist-check: installed-package resource parity failed", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print(
        f"dist-check: installed package resource parity OK "
        f"({len(actual)} runtime resources at {package_dir})"
    )
    return 0


def validate_artifacts(dist_dir: Path, source_root: Path) -> int:
    if not dist_dir.is_dir():
        print(f"dist-check: missing dist directory: {dist_dir}", file=sys.stderr)
        return 1

    wheels = sorted(dist_dir.glob("*.whl"))
    sdists = sorted(dist_dir.glob("*.tar.gz"))
    if not wheels or not sdists:
        print(
            "dist-check: expected at least one wheel and one .tar.gz sdist "
            f"under {dist_dir}",
            file=sys.stderr,
        )
        return 1

    try:
        expected = source_resources(source_root)
    except (OSError, ValueError) as exc:
        print(f"dist-check: {exc}", file=sys.stderr)
        return 1

    failures = validate_source_resources(expected)
    for artifact in [*wheels, *sdists]:
        if artifact.suffix == ".whl":
            names = list(iter_zip_names(artifact))
            resources = read_zip_resources(artifact)
            for name in names:
                normalised = name.replace("\\", "/")
                if normalised.startswith(BANNED_WHEEL_PREFIXES):
                    failures.append(
                        f"{artifact.name}: non-package file in wheel: {normalised}"
                    )
        else:
            names = list(iter_tar_names(artifact))
            resources = read_tar_resources(artifact)

        for violation in find_violations(names):
            failures.append(f"{artifact.name}: forbidden file: {violation}")
        for duplicate in find_duplicate_members(names):
            failures.append(f"{artifact.name}: duplicate archive member: {duplicate}")
        for duplicate in find_duplicate_resources(names):
            failures.append(f"{artifact.name}: duplicate runtime resource: {duplicate}")
        failures.extend(find_resource_failures(expected, resources, artifact.name))

    if failures:
        print("dist-check: artifact validation failed", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print(
        f"dist-check: wheel/sdist resource parity OK "
        f"({len(expected)} runtime resources)"
    )
    return 0


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.installed:
        return validate_installed(args.source_root)
    return validate_artifacts(args.dist_dir, args.source_root)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
