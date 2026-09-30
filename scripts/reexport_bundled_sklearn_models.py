#!/usr/bin/env python3
"""Re-export bundled sklearn/joblib artifacts to match the current runtime.

This reduces legacy scikit-learn unpickle warnings and removes reliance on
compatibility shims for old module paths.
"""

from __future__ import annotations

import argparse
import io
import json
import pickle
import warnings
from collections.abc import Iterable, Sequence
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_STORED, ZipFile, ZipInfo

import joblib

from lexnlp.ml.artifact_abi import (
    artifact_metadata,
    assert_model_artifact_runtime,
)
from lexnlp.ml.artifact_io import atomic_output_path, atomic_pickle_dump
from lexnlp.utils.unpickler import (
    CompatibilityReport,
    load_joblib_model,
    renamed_load,
)

if __package__:
    from ._artifact_transaction import publish_staged_files
else:
    from _artifact_transaction import publish_staged_files

BUNDLED_MODEL_PATHS: tuple[Path, ...] = (
    Path("lexnlp/extract/de/date_model.pickle"),
    Path("lexnlp/extract/de/model.pickle"),
    Path("lexnlp/extract/en/addresses/addresses_clf.pickle"),
    Path("lexnlp/extract/en/date_model.pickle"),
    Path("lexnlp/extract/ml/en/data/definition_model_layered.pickle.gzip"),
    Path("lexnlp/nlp/en/segments/page_segmenter.pickle"),
    Path("lexnlp/nlp/en/segments/paragraph_segmenter.pickle"),
    Path("lexnlp/nlp/en/segments/section_segmenter.pickle"),
    Path("lexnlp/nlp/en/segments/title_locator.pickle"),
)

LEGACY_WARNING_TOKEN = "Trying to unpickle estimator"


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Re-export bundled sklearn/joblib model artifacts in-place.",
    )
    parser.add_argument(
        "--paths",
        nargs="*",
        help="Optional explicit list of paths to re-export (defaults to known bundled models).",
    )
    parser.add_argument(
        "--compress",
        type=int,
        default=3,
        help="joblib compression level (default: 3).",
    )
    parser.add_argument(
        "--check-current",
        action="store_true",
        help="load and validate artifacts without rewriting them",
    )
    parser.add_argument(
        "--metadata-output",
        type=Path,
        help="write deterministic re-export provenance metadata as JSON",
    )
    return parser.parse_args(argv)


def iter_paths(args: argparse.Namespace) -> Iterable[Path]:
    if args.paths:
        for raw in args.paths:
            yield Path(raw)
    else:
        yield from BUNDLED_MODEL_PATHS


def load_model(path: Path, *, report: CompatibilityReport | None = None):
    # Most artifacts are joblib dumps; the address classifier is loaded via
    # RenameUnpickler for legacy sklearn module paths.
    if path.name == "addresses_clf.pickle":
        with path.open("rb") as f:
            try:
                return renamed_load(f, report=report)
            except Exception:
                # If the file was previously dumped with joblib, fall back so we
                # can re-export it into a plain pickle again.
                return load_joblib_model(path, report=report)
    return load_joblib_model(path, report=report)


def load_layered_definition_models(
    path: Path,
    *,
    report: CompatibilityReport | None = None,
):
    with ZipFile(path) as archive:
        payload = {}
        for name in ("term.pickle", "definition.pickle"):
            raw = archive.read(name)
            payload[name] = renamed_load(io.BytesIO(raw), report=report)
    return payload


def _write_layered_definition_models(path: Path, payload: dict[str, object]) -> None:
    with ZipFile(path, mode="w", compression=ZIP_STORED) as archive:
        for name in ("term.pickle", "definition.pickle"):
            serialized = pickle.dumps(
                payload[name],
                protocol=pickle.HIGHEST_PROTOCOL,
            )
            member = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            member.compress_type = ZIP_STORED
            archive.writestr(member, serialized)


def reexport_layered_definition_models(path: Path) -> None:
    payload = load_layered_definition_models(path)
    with atomic_output_path(path) as temporary_path:
        _write_layered_definition_models(temporary_path, payload)


def load_diagnostics(path: Path) -> tuple[int, int, int, int]:
    report = CompatibilityReport()
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        if path.name == "definition_model_layered.pickle.gzip":
            _ = load_layered_definition_models(path, report=report)
        else:
            _ = load_model(path, report=report)
    warning_count = sum(
        1 for item in captured if LEGACY_WARNING_TOKEN in str(item.message)
    )
    return (
        warning_count,
        report.legacy_tree_upgrades,
        report.classifier_value_normalizations,
        report.estimator_attribute_upgrades,
    )


def write_metadata(
    path: Path,
    model_paths: Sequence[Path],
    *,
    artifact_paths: Sequence[Path] | None = None,
) -> None:
    metadata_sources = model_paths if artifact_paths is None else artifact_paths
    if len(metadata_sources) != len(model_paths):
        raise ValueError("model_paths and artifact_paths must have equal lengths")

    artifacts = []
    runtime = None
    for model_path, artifact_path in zip(model_paths, metadata_sources):
        details = artifact_metadata(artifact_path)
        runtime = details.pop("runtime")
        details.pop("artifact_path")
        details["path"] = model_path.as_posix()
        artifacts.append(details)

    payload = {
        "schema_version": 1,
        "strategy": (
            "Scoped offline reconstruction of legacy sklearn tree node state "
            "and estimator attributes, plus classifier value normalization; "
            "runtime imports use only native sklearn objects."
        ),
        "runtime": runtime,
        "artifacts": artifacts,
        "validation": [
            "scripts/reexport_bundled_sklearn_models.py --check-current",
            "pytest lexnlp",
            "contract and contract-type model quality gates",
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_candidate(source: Path, candidate: Path, *, compress: int) -> None:
    if source.name == "definition_model_layered.pickle.gzip":
        payload = load_layered_definition_models(source)
        _write_layered_definition_models(candidate, payload)
        return

    model = load_model(source)
    if source.name == "addresses_clf.pickle":
        # Keep as a plain pickle so lexnlp.extract.en.addresses.addresses can
        # keep using RenameUnpickler for old module-path compatibility.
        atomic_pickle_dump(
            model,
            candidate,
            protocol=pickle.HIGHEST_PROTOCOL,
        )
    else:
        joblib.dump(model, candidate, compress=compress)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    if not args.check_current:
        assert_model_artifact_runtime()
    failures: list[str] = []
    model_paths = list(iter_paths(args))
    if args.metadata_output:
        metadata_identity = args.metadata_output.resolve(strict=False)
        model_identities = {
            path.resolve(strict=False)
            for path in model_paths
        }
        if metadata_identity in model_identities:
            raise ValueError(
                "Metadata output must differ from every model path: "
                f"{args.metadata_output}"
            )

    if args.check_current:
        for path in model_paths:
            if not path.exists():
                failures.append(f"missing: {path}")
                continue

            (
                before_warnings,
                before_upgrades,
                before_normalizations,
                before_attribute_upgrades,
            ) = load_diagnostics(path)
            print(
                f"reexport-check: {path} "
                f"legacy_warnings={before_warnings} "
                f"legacy_tree_upgrades={before_upgrades} "
                f"classifier_value_normalizations={before_normalizations} "
                f"estimator_attribute_upgrades={before_attribute_upgrades}"
            )
            if (
                before_warnings
                or before_upgrades
                or before_normalizations
                or before_attribute_upgrades
            ):
                failures.append(
                    f"legacy serialization remains in {path}: "
                    f"warnings={before_warnings}, tree_upgrades={before_upgrades}, "
                    f"classifier_value_normalizations={before_normalizations}, "
                    f"estimator_attribute_upgrades={before_attribute_upgrades}"
                )

        if failures:
            for failure in failures:
                print(f"reexport: ERROR {failure}")
            return 1
        if args.metadata_output:
            with TemporaryDirectory(
                prefix="lexnlp-bundled-reexport-metadata-"
            ) as temporary:
                staged_metadata = (
                    Path(temporary) / args.metadata_output.name
                )
                write_metadata(
                    staged_metadata,
                    model_paths,
                )
                publish_staged_files(
                    ((args.metadata_output, staged_metadata),)
                )
            print(f"reexport: wrote metadata: {args.metadata_output}")
        return 0

    with TemporaryDirectory(prefix="lexnlp-bundled-reexport-") as temporary:
        staging_root = Path(temporary)
        staged_models: list[tuple[Path, Path]] = []

        for index, path in enumerate(model_paths):
            if not path.exists():
                failures.append(f"missing: {path}")
                continue

            (
                before_warnings,
                before_upgrades,
                before_normalizations,
                before_attribute_upgrades,
            ) = load_diagnostics(path)

            candidate_dir = staging_root / str(index)
            candidate_dir.mkdir(parents=True)
            candidate_path = candidate_dir / path.name
            _write_candidate(path, candidate_path, compress=args.compress)

            (
                after_warnings,
                after_upgrades,
                after_normalizations,
                after_attribute_upgrades,
            ) = load_diagnostics(candidate_path)
            print(
                f"reexport: {path} "
                f"legacy_warnings before={before_warnings} "
                f"after={after_warnings} "
                f"legacy_tree_upgrades before={before_upgrades} "
                f"after={after_upgrades} "
                f"classifier_value_normalizations "
                f"before={before_normalizations} "
                f"after={after_normalizations} "
                f"estimator_attribute_upgrades "
                f"before={before_attribute_upgrades} "
                f"after={after_attribute_upgrades}"
            )
            if (
                after_warnings
                or after_upgrades
                or after_normalizations
                or after_attribute_upgrades
            ):
                failures.append(
                    f"re-export did not produce a current artifact for {path}: "
                    f"warnings={after_warnings}, "
                    f"tree_upgrades={after_upgrades}, "
                    "classifier_value_normalizations="
                    f"{after_normalizations}, "
                    "estimator_attribute_upgrades="
                    f"{after_attribute_upgrades}"
                )
            staged_models.append((path, candidate_path))

        if failures:
            for failure in failures:
                print(f"reexport: ERROR {failure}")
            return 1

        publications = list(staged_models)
        if args.metadata_output:
            staged_metadata = staging_root / "metadata" / args.metadata_output.name
            write_metadata(
                staged_metadata,
                model_paths,
                artifact_paths=[
                    candidate for _, candidate in staged_models
                ],
            )
            publications.append((args.metadata_output, staged_metadata))

        publish_staged_files(publications)

    if args.metadata_output:
        print(f"reexport: wrote metadata: {args.metadata_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__('sys').argv[1:]))
