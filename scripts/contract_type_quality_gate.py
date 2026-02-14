#!/usr/bin/env python3
"""Quality gate for contract-type model upgrades."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple


DEFAULT_FIXTURE = Path(
    "test_data/lexnlp/extract/en/contracts/tests/test_contracts/test_contract_type.csv"
)
REQUIRED_METRIC_KEYS = ("accuracy_top1", "accuracy_topn", "f1_macro", "f1_weighted")


def resolve_contract_type_model_tag() -> str:
    return (
        os.getenv("LEXNLP_CONTRACT_TYPE_MODEL_TAG")
        or "pipeline/contract-type/0.2-runtime"
    ).strip()


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare baseline and candidate contract-type models on a labeled fixture.",
    )
    parser.add_argument(
        "--baseline-tag",
        default=resolve_contract_type_model_tag(),
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
        "--top-n",
        type=int,
        default=3,
        help="Top-N used for accuracy_topN checks (default: 3).",
    )
    parser.add_argument(
        "--max-accuracy-top1-regression",
        type=float,
        default=0.0,
        help="Maximum allowed candidate top-1 accuracy drop vs baseline.",
    )
    parser.add_argument(
        "--max-accuracy-top3-regression",
        type=float,
        dest="max_accuracy_topn_regression",
        default=None,
        help="Deprecated alias for --max-accuracy-topn-regression (when --top-n=3).",
    )
    parser.add_argument(
        "--max-accuracy-topn-regression",
        type=float,
        default=0.0,
        help="Maximum allowed candidate top-N accuracy drop vs baseline.",
    )
    parser.add_argument(
        "--max-f1-macro-regression",
        type=float,
        default=0.0,
        help="Maximum allowed candidate macro-F1 drop vs baseline.",
    )
    parser.add_argument(
        "--max-f1-weighted-regression",
        type=float,
        default=0.0,
        help="Maximum allowed candidate weighted-F1 drop vs baseline.",
    )
    parser.add_argument(
        "--min-candidate-accuracy-top1",
        type=float,
        default=0.0,
        help="Absolute minimum candidate top-1 accuracy.",
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
            "(baseline_tag, fixture, top_n, metrics)."
        ),
    )
    return parser.parse_args(argv)


def load_fixture(path: Path) -> Tuple[List[str], List[str]]:
    if not path.exists():
        raise FileNotFoundError(f"Fixture file not found: {path}")

    texts: List[str] = []
    labels: List[str] = []

    with path.open("r", encoding="utf-8", newline="") as fixture_file:
        reader = csv.DictReader(fixture_file)
        for row in reader:
            text = (row.get("Text") or "").strip()
            label = (row.get("Contract_Type") or "").strip()
            if not text:
                raise ValueError("Fixture row missing Text")
            if not label:
                raise ValueError("Fixture row missing Contract_Type")
            texts.append(text)
            labels.append(label)

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


def score_pipeline(pipeline, texts: List[str], labels: List[str], *, top_n: int) -> Dict[str, float]:
    import numpy as np
    from sklearn.metrics import accuracy_score, f1_score

    top_n = max(1, int(top_n))

    pred_top1 = pipeline.predict(texts)
    accuracy_top1 = float(accuracy_score(labels, pred_top1))
    f1_macro = float(f1_score(labels, pred_top1, average="macro", zero_division=0))
    f1_weighted = float(f1_score(labels, pred_top1, average="weighted", zero_division=0))

    if not hasattr(pipeline, "predict_proba"):
        raise ValueError("Pipeline does not expose predict_proba; cannot compute top-N accuracy.")

    probas = pipeline.predict_proba(texts)
    classes = getattr(pipeline, "classes_", None)
    if classes is None:
        raise ValueError("Pipeline is missing classes_.")

    classes = np.asarray(classes)
    top_indices = np.argsort(probas, axis=1)[:, -top_n:]
    hits = 0
    for truth, indices in zip(labels, top_indices):
        if truth in set(classes[indices].tolist()):
            hits += 1
    accuracy_topn = float(hits / len(labels))

    return {
        "accuracy_top1": accuracy_top1,
        "accuracy_topn": accuracy_topn,
        "f1_macro": f1_macro,
        "f1_weighted": f1_weighted,
    }


def parse_metrics(raw: Dict[str, Any], source: str) -> Dict[str, float]:
    raw = dict(raw)
    # Backward compatibility: older baseline JSON used accuracy_top3.
    if "accuracy_topn" not in raw and "accuracy_top3" in raw:
        raw["accuracy_topn"] = raw["accuracy_top3"]

    missing = [key for key in REQUIRED_METRIC_KEYS if key not in raw]
    if missing:
        raise ValueError(f"Missing metric keys in {source}: {', '.join(missing)}")

    return {key: float(raw[key]) for key in REQUIRED_METRIC_KEYS}


def load_baseline_metrics(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Baseline metrics file not found: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Baseline metrics JSON must be an object")

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
        "top_n": payload.get("top_n"),
        "raw": payload,
    }


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    if args.top_n <= 0:
        raise ValueError("--top-n must be > 0")

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

        file_top_n = baseline_metrics_file.get("top_n")
        if file_top_n is not None and int(file_top_n) != int(args.top_n):
            raise ValueError(
                "top_n mismatch between CLI and baseline metrics JSON: "
                f"{args.top_n} != {file_top_n}"
            )
    else:
        baseline_metrics = score_pipeline(
            load_pipeline_for_tag(args.baseline_tag),
            texts,
            labels,
            top_n=args.top_n,
        )

    candidate_metrics = score_pipeline(
        load_pipeline_for_tag(args.candidate_tag),
        texts,
        labels,
        top_n=args.top_n,
    )

    result = {
        "baseline_tag": args.baseline_tag,
        "candidate_tag": args.candidate_tag,
        "fixture": str(args.fixture),
        "top_n": int(args.top_n),
        "baseline_source": baseline_source,
        "baseline_metrics_json": baseline_metrics_source,
        "baseline": baseline_metrics,
        "candidate": candidate_metrics,
        "checks": [],
        "passed": True,
    }

    def require(metric_key: str, max_regression: float) -> None:
        baseline_value = float(baseline_metrics[metric_key])
        candidate_value = float(candidate_metrics[metric_key])
        delta = candidate_value - baseline_value
        passed = delta >= -max_regression
        result["checks"].append(
            {
                "metric": metric_key,
                "baseline": baseline_value,
                "candidate": candidate_value,
                "delta": delta,
                "max_regression": max_regression,
                "passed": passed,
            }
        )
        result["passed"] = bool(result["passed"] and passed)

    require("accuracy_top1", args.max_accuracy_top1_regression)
    require("accuracy_topn", args.max_accuracy_topn_regression)
    require("f1_macro", args.max_f1_macro_regression)
    require("f1_weighted", args.max_f1_weighted_regression)

    if candidate_metrics["accuracy_top1"] < args.min_candidate_accuracy_top1:
        result["checks"].append(
            {
                "metric": "min_candidate_accuracy_top1",
                "candidate": float(candidate_metrics["accuracy_top1"]),
                "min_required": float(args.min_candidate_accuracy_top1),
                "passed": False,
            }
        )
        result["passed"] = False

    if args.write_baseline_metrics_json:
        baseline_payload = {
            "baseline_tag": args.baseline_tag,
            "fixture": str(args.fixture),
            "top_n": int(args.top_n),
            "metrics": baseline_metrics,
        }
        args.write_baseline_metrics_json.parent.mkdir(parents=True, exist_ok=True)
        args.write_baseline_metrics_json.write_text(
            json.dumps(baseline_payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(
            json.dumps(result, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
