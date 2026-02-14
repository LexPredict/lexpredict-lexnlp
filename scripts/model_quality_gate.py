#!/usr/bin/env python3
"""Quality gate for contract-classifier model upgrades."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple


DEFAULT_FIXTURE = Path(
    "test_data/lexnlp/extract/en/contracts/tests/test_contracts/test_is_contract.csv"
)
REQUIRED_METRIC_KEYS = ("accuracy", "f1", "precision", "recall")


def resolve_contract_model_tag() -> str:
    return (
        os.getenv("LEXNLP_CONTRACT_MODEL_TAG")
        or os.getenv("LEXNLP_IS_CONTRACT_MODEL_TAG")
        or "pipeline/is-contract/0.1"
    ).strip()


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare baseline and candidate contract models on a labeled fixture.",
    )
    parser.add_argument(
        "--baseline-tag",
        default=resolve_contract_model_tag(),
        help="Catalog tag used as baseline model.",
    )
    parser.add_argument(
        "--baseline-metrics-json",
        type=Path,
        help=(
            "Optional path to committed baseline metrics JSON. "
            "When provided, baseline metrics are loaded from this file "
            "instead of executing the baseline model."
        ),
    )
    parser.add_argument(
        "--baseline-metrics-tolerance",
        type=float,
        default=1e-9,
        help="Tolerance for fixture/probability checks when baseline metrics JSON is used.",
    )
    parser.add_argument(
        "--candidate-tag",
        required=True,
        help="Catalog tag used as candidate model.",
    )
    parser.add_argument(
        "--fixture",
        type=Path,
        default=DEFAULT_FIXTURE,
        help=f"CSV fixture path (default: {DEFAULT_FIXTURE})",
    )
    parser.add_argument(
        "--min-probability",
        type=float,
        default=0.3,
        help="Classification threshold used by is_contract.",
    )
    parser.add_argument(
        "--max-accuracy-regression",
        type=float,
        default=0.0,
        help="Maximum allowed candidate accuracy drop vs baseline.",
    )
    parser.add_argument(
        "--max-f1-regression",
        type=float,
        default=0.0,
        help="Maximum allowed candidate F1 drop vs baseline.",
    )
    parser.add_argument(
        "--min-candidate-accuracy",
        type=float,
        default=0.0,
        help="Absolute minimum candidate accuracy.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        help="Optional path to write JSON results.",
    )
    parser.add_argument(
        "--write-baseline-metrics-json",
        type=Path,
        help=(
            "Optional path to write canonical baseline metrics JSON "
            "(baseline_tag, fixture, min_probability, metrics)."
        ),
    )
    return parser.parse_args(argv)


def load_fixture(path: Path) -> Tuple[List[str], List[bool]]:
    if not path.exists():
        raise FileNotFoundError(f"Fixture file not found: {path}")

    texts: List[str] = []
    labels: List[bool] = []

    with path.open("r", encoding="utf-8", newline="") as fixture_file:
        reader = csv.DictReader(fixture_file)
        for row in reader:
            text = row["Text"]
            label_raw = row["Is_Contract"].strip().lower()
            if label_raw not in {"true", "false"}:
                raise ValueError(f"Unexpected label value: {row['Is_Contract']}")
            texts.append(text)
            labels.append(label_raw == "true")

    if not texts:
        raise ValueError(f"Fixture file contains no rows: {path}")
    return texts, labels


def ensure_tag_downloaded(tag: str) -> Path:
    from lexnlp.ml.catalog import get_path_from_catalog
    from lexnlp.ml.catalog.download import download_github_release

    try:
        return get_path_from_catalog(tag)
    except FileNotFoundError:
        download_github_release(tag, prompt_user=False)
        return get_path_from_catalog(tag)


def load_pipeline_for_tag(tag: str):
    from cloudpickle import load

    model_path = ensure_tag_downloaded(tag)
    with model_path.open("rb") as model_file:
        return load(model_file)


def score_pipeline(pipeline, texts: List[str], labels: List[bool], min_probability: float) -> Dict[str, float]:
    from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
    from lexnlp.extract.en.contracts.predictors import ProbabilityPredictorIsContract

    predictor = ProbabilityPredictorIsContract(pipeline=pipeline)
    predictions = [
        bool(predictor.is_contract(text=text, min_probability=min_probability))
        for text in texts
    ]
    return {
        "accuracy": float(accuracy_score(labels, predictions)),
        "f1": float(f1_score(labels, predictions)),
        "precision": float(precision_score(labels, predictions, zero_division=0)),
        "recall": float(recall_score(labels, predictions, zero_division=0)),
    }


def parse_metrics(raw: Dict[str, Any], source: str) -> Dict[str, float]:
    missing = [key for key in REQUIRED_METRIC_KEYS if key not in raw]
    if missing:
        raise ValueError(f"Missing metric keys in {source}: {', '.join(missing)}")

    return {
        key: float(raw[key])
        for key in REQUIRED_METRIC_KEYS
    }


def load_baseline_metrics(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Baseline metrics file not found: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Baseline metrics JSON must be an object")

    # Accept either a dedicated "metrics" object or the full quality-gate output shape.
    if "metrics" in payload:
        metrics = parse_metrics(payload["metrics"], f"{path}::metrics")
    elif "baseline" in payload:
        metrics = parse_metrics(payload["baseline"], f"{path}::baseline")
    else:
        raise ValueError(
            f"Baseline metrics JSON must contain either 'metrics' or 'baseline': {path}"
        )

    return {
        "metrics": metrics,
        "baseline_tag": payload.get("baseline_tag"),
        "fixture": payload.get("fixture"),
        "min_probability": payload.get("min_probability"),
        "raw": payload,
    }


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    texts, labels = load_fixture(args.fixture)

    baseline_source = "tag"
    baseline_metrics_source = None
    baseline_metrics_file: Dict[str, Any] | None = None

    if args.baseline_metrics_json:
        baseline_source = "metrics-json"
        baseline_metrics_source = str(args.baseline_metrics_json)
        baseline_metrics_file = load_baseline_metrics(args.baseline_metrics_json)
        baseline_metrics = baseline_metrics_file["metrics"]

        file_baseline_tag = baseline_metrics_file.get("baseline_tag")
        if file_baseline_tag and file_baseline_tag != args.baseline_tag:
            raise ValueError(
                "Baseline tag mismatch between --baseline-tag and --baseline-metrics-json: "
                f"{args.baseline_tag!r} != {file_baseline_tag!r}"
            )

        file_fixture = baseline_metrics_file.get("fixture")
        if file_fixture:
            expected_fixture = str(args.fixture)
            if file_fixture != expected_fixture:
                raise ValueError(
                    "Fixture mismatch between --fixture and --baseline-metrics-json: "
                    f"{expected_fixture!r} != {file_fixture!r}"
                )

        file_min_probability = baseline_metrics_file.get("min_probability")
        if file_min_probability is not None:
            if abs(float(file_min_probability) - args.min_probability) > args.baseline_metrics_tolerance:
                raise ValueError(
                    "min_probability mismatch between CLI and baseline metrics JSON: "
                    f"{args.min_probability} != {file_min_probability}"
                )
    else:
        baseline_metrics = score_pipeline(
            load_pipeline_for_tag(args.baseline_tag),
            texts,
            labels,
            args.min_probability,
        )

    candidate_metrics = score_pipeline(
        load_pipeline_for_tag(args.candidate_tag),
        texts,
        labels,
        args.min_probability,
    )

    result = {
        "baseline_tag": args.baseline_tag,
        "candidate_tag": args.candidate_tag,
        "fixture": str(args.fixture),
        "min_probability": args.min_probability,
        "baseline_source": baseline_source,
        "baseline_metrics_json": baseline_metrics_source,
        "baseline": baseline_metrics,
        "candidate": candidate_metrics,
    }

    print(json.dumps(result, indent=2, sort_keys=True))

    violations: List[str] = []
    accuracy_drop = baseline_metrics["accuracy"] - candidate_metrics["accuracy"]
    f1_drop = baseline_metrics["f1"] - candidate_metrics["f1"]

    if accuracy_drop > args.max_accuracy_regression:
        violations.append(
            "accuracy regression exceeds threshold "
            f"({accuracy_drop:.6f} > {args.max_accuracy_regression:.6f})"
        )
    if f1_drop > args.max_f1_regression:
        violations.append(
            f"f1 regression exceeds threshold ({f1_drop:.6f} > {args.max_f1_regression:.6f})"
        )
    if candidate_metrics["accuracy"] < args.min_candidate_accuracy:
        violations.append(
            "candidate accuracy below minimum "
            f"({candidate_metrics['accuracy']:.6f} < {args.min_candidate_accuracy:.6f})"
        )

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

    if args.write_baseline_metrics_json:
        baseline_payload = {
            "baseline_tag": args.baseline_tag,
            "fixture": str(args.fixture),
            "metrics": baseline_metrics,
            "min_probability": args.min_probability,
        }
        args.write_baseline_metrics_json.parent.mkdir(parents=True, exist_ok=True)
        args.write_baseline_metrics_json.write_text(
            json.dumps(baseline_payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    if violations:
        for violation in violations:
            print(f"QUALITY GATE VIOLATION: {violation}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
