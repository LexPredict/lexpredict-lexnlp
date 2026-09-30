#!/usr/bin/env python3
"""Re-export the contract classifier model under a new catalog tag."""

from __future__ import annotations

import argparse
import json
import os
import pickle
import shutil
import subprocess
import sys
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from lexnlp.ml.artifact_io import atomic_pickle_dump

if __package__:
    from ._artifact_transaction import publish_staged_files
else:
    from _artifact_transaction import publish_staged_files

DEFAULT_FIXTURE = Path(
    "test_data/lexnlp/extract/en/contracts/tests/test_contracts/test_is_contract.csv"
)
DEFAULT_BASELINE_METRICS = Path(
    "test_data/model_quality/is_contract_baseline_metrics.json"
)
LEGACY_WARNING_TOKEN = "Trying to unpickle estimator"


def resolve_contract_model_tag() -> str:
    return (
        os.getenv("LEXNLP_CONTRACT_MODEL_TAG")
        or os.getenv("LEXNLP_IS_CONTRACT_MODEL_TAG")
        or "pipeline/is-contract/0.1"
    ).strip()


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Load an existing contract classifier tag and re-serialize it with "
            "the current runtime under a new tag."
        )
    )
    parser.add_argument(
        "--source-tag",
        default=resolve_contract_model_tag(),
        help="Source model tag to load from LexNLP catalog.",
    )
    parser.add_argument(
        "--target-tag",
        required=True,
        help="Destination model tag to write under LexNLP catalog.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite destination artifact if it already exists.",
    )
    parser.add_argument(
        "--skip-quality-gate",
        action="store_true",
        help="Skip post-export quality-gate execution.",
    )
    parser.add_argument(
        "--fixture",
        type=Path,
        default=DEFAULT_FIXTURE,
        help=f"Fixture CSV used by quality gate (default: {DEFAULT_FIXTURE}).",
    )
    parser.add_argument(
        "--baseline-metrics-json",
        type=Path,
        default=DEFAULT_BASELINE_METRICS,
        help=(
            "Baseline metrics JSON for quality gate. "
            f"Default: {DEFAULT_BASELINE_METRICS}"
        ),
    )
    parser.add_argument(
        "--max-accuracy-regression",
        type=float,
        default=0.0,
        help="Maximum allowed candidate accuracy drop.",
    )
    parser.add_argument(
        "--max-f1-regression",
        type=float,
        default=0.0,
        help="Maximum allowed candidate F1 drop.",
    )
    parser.add_argument(
        "--min-probability",
        type=float,
        default=0.3,
        help="Probability threshold used by model quality gate.",
    )
    parser.add_argument(
        "--output-metadata-json",
        type=Path,
        help=(
            "Optional explicit path for metadata JSON. "
            "Defaults to artifacts/model_reexports/<target-tag>.metadata.json."
        ),
    )
    parser.add_argument(
        "--max-legacy-warning-regression",
        type=int,
        default=0,
        help=(
            "Maximum allowed increase in legacy sklearn unpickle warning count "
            "between source and candidate model."
        ),
    )
    return parser.parse_args(argv)


def ensure_tag_downloaded(tag: str) -> Path:
    if __package__:
        from ._model_assets import ensure_tag_downloaded as ensure_verified_tag
    else:
        from _model_assets import ensure_tag_downloaded as ensure_verified_tag

    return ensure_verified_tag(tag)


def run_quality_gate(
    *,
    source_tag: str,
    target_tag: str,
    fixture: Path,
    baseline_metrics_json: Path,
    min_probability: float,
    max_accuracy_regression: float,
    max_f1_regression: float,
) -> None:
    gate_script = Path(__file__).with_name("model_quality_gate.py")
    cmd = [
        sys.executable,
        str(gate_script),
        "--baseline-tag",
        source_tag,
        "--candidate-tag",
        target_tag,
        "--fixture",
        str(fixture),
        "--min-probability",
        str(min_probability),
        "--max-accuracy-regression",
        str(max_accuracy_regression),
        "--max-f1-regression",
        str(max_f1_regression),
    ]

    if baseline_metrics_json.exists():
        cmd.extend(["--baseline-metrics-json", str(baseline_metrics_json)])

    subprocess.run(cmd, check=True)


def get_legacy_warning_messages(model_path: Path) -> list[str]:
    probe_code = """
import json
import sys
import warnings
from pathlib import Path
from lexnlp.utils.unpickler import load_sklearn_model

token = sys.argv[2]
path = Path(sys.argv[1])
with warnings.catch_warnings(record=True) as captured:
    warnings.simplefilter("always")
    with path.open("rb") as model_file:
        load_sklearn_model(model_file)

messages = [
    str(item.message).splitlines()[0]
    for item in captured
    if token in str(item.message)
]
print(json.dumps(messages))
"""
    result = subprocess.run(
        [sys.executable, "-c", probe_code, str(model_path), LEGACY_WARNING_TOKEN],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout.strip() or "[]")


def _stage_catalog_artifact(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(source, destination, follow_symlinks=False)
    except OSError:
        shutil.copy2(source, destination)


@contextmanager
def isolated_quality_gate_catalog(
    *,
    source_tag: str,
    target_tag: str,
    source_path: Path,
    candidate_path: Path,
) -> Iterator[None]:
    """Expose a candidate to the tag-based gate without publishing it."""
    with TemporaryDirectory(prefix="lexnlp-contract-quality-gate-") as temporary:
        nltk_data_root = Path(temporary)
        catalog_root = nltk_data_root / "lexpredict-lexnlp"
        _stage_catalog_artifact(
            source_path,
            catalog_root / source_tag / source_path.name,
        )
        _stage_catalog_artifact(
            candidate_path,
            catalog_root / target_tag / source_path.name,
        )

        had_nltk_data = "NLTK_DATA" in os.environ
        previous_nltk_data = os.environ.get("NLTK_DATA")
        nltk_data_paths = [str(nltk_data_root)]
        if previous_nltk_data:
            nltk_data_paths.append(previous_nltk_data)
        os.environ["NLTK_DATA"] = os.pathsep.join(nltk_data_paths)
        try:
            yield
        finally:
            if had_nltk_data:
                assert previous_nltk_data is not None
                os.environ["NLTK_DATA"] = previous_nltk_data
            else:
                os.environ.pop("NLTK_DATA", None)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    if args.source_tag == args.target_tag:
        raise ValueError("--source-tag and --target-tag must differ")

    from lexnlp.extract.en.contracts.predictors import ProbabilityPredictorIsContract
    from lexnlp.ml.artifact_abi import (
        artifact_metadata,
        assert_model_artifact_runtime,
    )
    from lexnlp.ml.catalog import CATALOG
    from lexnlp.utils.unpickler import load_sklearn_model

    assert_model_artifact_runtime()

    source_path = ensure_tag_downloaded(args.source_tag)
    destination_dir = CATALOG / args.target_tag
    destination_path = destination_dir / source_path.name

    if destination_path.exists() and not args.force:
        raise FileExistsError(
            f"Destination already exists: {destination_path} "
            "(use --force to overwrite)."
        )

    destination_dir.mkdir(parents=True, exist_ok=True)

    with source_path.open("rb") as source_file:
        pipeline = load_sklearn_model(source_file)

    # Validate and apply runtime compatibility patches before re-serializing.
    ProbabilityPredictorIsContract(pipeline=pipeline)

    default_metadata_path = Path("artifacts/model_reexports") / (
        f"{args.target_tag.replace('/', '__')}.metadata.json"
    )
    metadata_path = args.output_metadata_json or default_metadata_path
    metadata_identity = metadata_path.resolve(strict=False)
    if metadata_identity in {
        source_path.resolve(strict=False),
        destination_path.resolve(strict=False),
    }:
        raise ValueError(
            "Metadata output must differ from the source and destination "
            f"model paths: {metadata_path}"
        )

    quality_gate_message = (
        "re-export: skipping quality gate by request"
        if args.skip_quality_gate
        else "re-export: quality gate passed"
    )
    with TemporaryDirectory(prefix="lexnlp-contract-reexport-") as temporary:
        staging_root = Path(temporary)
        candidate_path = staging_root / source_path.name

        # Use stdlib pickle so sklearn writes current runtime metadata. Reload
        # the exact candidate bytes before any destination becomes visible.
        atomic_pickle_dump(
            pipeline,
            candidate_path,
            protocol=pickle.HIGHEST_PROTOCOL,
        )
        with candidate_path.open("rb") as candidate_file:
            candidate_pipeline = load_sklearn_model(candidate_file)
        ProbabilityPredictorIsContract(pipeline=candidate_pipeline)

        source_legacy_warning_messages = get_legacy_warning_messages(source_path)
        candidate_legacy_warning_messages = get_legacy_warning_messages(
            candidate_path
        )
        source_legacy_warning_count = len(source_legacy_warning_messages)
        candidate_legacy_warning_count = len(candidate_legacy_warning_messages)
        warning_summary = (
            "re-export: legacy sklearn warnings "
            f"(source={source_legacy_warning_count}, "
            f"candidate={candidate_legacy_warning_count})"
        )

        warning_regression = (
            candidate_legacy_warning_count - source_legacy_warning_count
        )
        if warning_regression > args.max_legacy_warning_regression:
            print(warning_summary)
            print(
                "re-export: legacy warning regression exceeds threshold "
                f"({warning_regression} > "
                f"{args.max_legacy_warning_regression})"
            )
            if candidate_legacy_warning_messages:
                print("re-export: candidate legacy warnings:")
                for message in candidate_legacy_warning_messages:
                    print(f"  - {message}")
            return 1

        print(warning_summary)
        if not args.skip_quality_gate:
            with isolated_quality_gate_catalog(
                source_tag=args.source_tag,
                target_tag=args.target_tag,
                source_path=source_path,
                candidate_path=candidate_path,
            ):
                run_quality_gate(
                    source_tag=args.source_tag,
                    target_tag=args.target_tag,
                    fixture=args.fixture,
                    baseline_metrics_json=args.baseline_metrics_json,
                    min_probability=args.min_probability,
                    max_accuracy_regression=args.max_accuracy_regression,
                    max_f1_regression=args.max_f1_regression,
                )

        artifact_details = artifact_metadata(candidate_path)
        artifact_details["artifact_path"] = str(destination_path)
        metadata_payload = {
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "source_tag": args.source_tag,
            "target_tag": args.target_tag,
            "source_model_path": str(source_path),
            "target_model_path": str(destination_path),
            "fixture": str(args.fixture),
            "min_probability": args.min_probability,
            **artifact_details,
        }
        staged_metadata_path = staging_root / "metadata" / metadata_path.name
        staged_metadata_path.parent.mkdir(parents=True, exist_ok=True)
        staged_metadata_path.write_text(
            json.dumps(metadata_payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        publish_staged_files(
            (
                (destination_path, candidate_path),
                (metadata_path, staged_metadata_path),
            )
        )

    print(f"re-export: wrote model to {destination_path}")
    print(f"re-export: wrote metadata to {metadata_path}")
    print(quality_gate_message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
