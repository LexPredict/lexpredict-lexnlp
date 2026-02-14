#!/usr/bin/env python3
"""Re-export the contract classifier model under a new catalog tag."""

from __future__ import annotations

import argparse
import json
import os
import pickle
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from cloudpickle import load


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
    from lexnlp.ml.catalog import get_path_from_catalog
    from lexnlp.ml.catalog.download import download_github_release

    try:
        return get_path_from_catalog(tag)
    except FileNotFoundError:
        download_github_release(tag, prompt_user=False)
        return get_path_from_catalog(tag)


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
from cloudpickle import load

token = sys.argv[2]
path = Path(sys.argv[1])
with warnings.catch_warnings(record=True) as captured:
    warnings.simplefilter("always")
    with path.open("rb") as model_file:
        load(model_file)

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


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    if args.source_tag == args.target_tag:
        raise ValueError("--source-tag and --target-tag must differ")

    from lexnlp import __version__ as lexnlp_version
    from lexnlp.extract.en.contracts.predictors import ProbabilityPredictorIsContract
    from lexnlp.ml.catalog import CATALOG
    from sklearn import __version__ as sklearn_version

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
        pipeline = load(source_file)

    # Validate and apply runtime compatibility patches before re-serializing.
    ProbabilityPredictorIsContract(pipeline=pipeline)

    # Use stdlib pickle for re-export so sklearn writes current runtime metadata.
    with destination_path.open("wb") as destination_file:
        pickle.dump(pipeline, destination_file)

    default_metadata_path = Path("artifacts/model_reexports") / (
        f"{args.target_tag.replace('/', '__')}.metadata.json"
    )
    metadata_path = args.output_metadata_json or default_metadata_path
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_payload = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_tag": args.source_tag,
        "target_tag": args.target_tag,
        "source_model_path": str(source_path),
        "target_model_path": str(destination_path),
        "fixture": str(args.fixture),
        "min_probability": args.min_probability,
        "runtime": {
            "python": sys.version.split()[0],
            "scikit_learn": sklearn_version,
            "lexnlp": lexnlp_version,
        },
    }
    metadata_path.write_text(
        json.dumps(metadata_payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    print(f"re-export: wrote model to {destination_path}")
    print(f"re-export: wrote metadata to {metadata_path}")

    source_legacy_warning_messages = get_legacy_warning_messages(source_path)
    candidate_legacy_warning_messages = get_legacy_warning_messages(destination_path)
    source_legacy_warning_count = len(source_legacy_warning_messages)
    candidate_legacy_warning_count = len(candidate_legacy_warning_messages)
    print(
        "re-export: legacy sklearn warnings "
        f"(source={source_legacy_warning_count}, candidate={candidate_legacy_warning_count})"
    )

    warning_regression = candidate_legacy_warning_count - source_legacy_warning_count
    if warning_regression > args.max_legacy_warning_regression:
        print(
            "re-export: legacy warning regression exceeds threshold "
            f"({warning_regression} > {args.max_legacy_warning_regression})"
        )
        if candidate_legacy_warning_messages:
            print("re-export: candidate legacy warnings:")
            for message in candidate_legacy_warning_messages:
                print(f"  - {message}")
        return 1

    if args.skip_quality_gate:
        print("re-export: skipping quality gate by request")
    else:
        run_quality_gate(
            source_tag=args.source_tag,
            target_tag=args.target_tag,
            fixture=args.fixture,
            baseline_metrics_json=args.baseline_metrics_json,
            min_probability=args.min_probability,
            max_accuracy_regression=args.max_accuracy_regression,
            max_f1_regression=args.max_f1_regression,
        )
        print("re-export: quality gate passed")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
