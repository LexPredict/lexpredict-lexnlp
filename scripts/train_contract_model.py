#!/usr/bin/env python3
"""Train and validate a contract-classifier candidate from released corpora."""

from __future__ import annotations

import argparse
import copy
import json
import pickle
import subprocess
import sys
import tarfile
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from cloudpickle import load
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline


DEFAULT_POSITIVE_TAGS: Tuple[str, ...] = (
    "corpus/contract-types/0.1",
    "corpus/atticus-cuad-v1-plaintext/0.1",
)
DEFAULT_NEGATIVE_TAGS: Tuple[str, ...] = (
    "corpus/uspto-sample/0.1",
    "corpus/sec-edgar-forms-3-4-5-8k-10k-sample/0.1",
    "corpus/arxiv-abstracts-with-agreement/0.1",
    "corpus/eurlex-sample-10000/0.1",
)
DEFAULT_BASELINE_METRICS = Path("test_data/model_quality/is_contract_baseline_metrics.json")
DEFAULT_FIXTURE = Path(
    "test_data/lexnlp/extract/en/contracts/tests/test_contracts/test_is_contract.csv"
)


class TrainingError(Exception):
    """Raised for unrecoverable training pipeline errors."""


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Train a contract-model candidate by reusing LexNLP baseline preprocessing/"
            "vectorization steps and replacing the classifier."
        )
    )
    parser.add_argument(
        "--baseline-tag",
        default="pipeline/is-contract/0.1",
        help="Existing pipeline tag used as feature-extractor baseline.",
    )
    parser.add_argument(
        "--candidate-tag",
        default="pipeline/is-contract/0.2",
        help="Catalog tag where the candidate artifact will be written.",
    )
    parser.add_argument(
        "--positive-tags",
        nargs="+",
        default=list(DEFAULT_POSITIVE_TAGS),
        help="Corpus tags labeled as contracts.",
    )
    parser.add_argument(
        "--negative-tags",
        nargs="+",
        default=list(DEFAULT_NEGATIVE_TAGS),
        help="Corpus tags labeled as non-contracts.",
    )
    parser.add_argument(
        "--max-docs-per-tag",
        type=int,
        default=800,
        help="Maximum documents extracted from each corpus tag.",
    )
    parser.add_argument(
        "--head-character-n",
        type=int,
        default=4000,
        help="Maximum characters read from each document.",
    )
    parser.add_argument(
        "--validation-size",
        type=float,
        default=0.2,
        help="Validation split ratio for estimator selection.",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=7,
        help="Random seed for train/validation split and estimators.",
    )
    parser.add_argument(
        "--estimators",
        nargs="+",
        default=("gaussian_nb", "logistic_regression", "random_forest"),
        choices=("gaussian_nb", "logistic_regression", "random_forest"),
        help="Estimator candidates to train and compare.",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Worker count for random-forest training.",
    )
    parser.add_argument(
        "--min-probability",
        type=float,
        default=0.3,
        help="Probability threshold used for metrics and quality gate.",
    )
    parser.add_argument(
        "--max-accuracy-regression",
        type=float,
        default=0.0,
        help="Quality gate max allowed candidate accuracy drop.",
    )
    parser.add_argument(
        "--max-f1-regression",
        type=float,
        default=0.0,
        help="Quality gate max allowed candidate F1 drop.",
    )
    parser.add_argument(
        "--baseline-metrics-json",
        type=Path,
        default=DEFAULT_BASELINE_METRICS,
        help=(
            "Committed baseline metrics JSON consumed by quality gate "
            f"(default: {DEFAULT_BASELINE_METRICS})."
        ),
    )
    parser.add_argument(
        "--fixture",
        type=Path,
        default=DEFAULT_FIXTURE,
        help=f"Fixed evaluation fixture for quality gate (default: {DEFAULT_FIXTURE}).",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("artifacts/model_training/contract_model_training_report.json"),
        help="Path for detailed training report JSON.",
    )
    parser.add_argument(
        "--skip-quality-gate",
        action="store_true",
        help="Skip model_quality_gate.py validation.",
    )
    parser.add_argument(
        "--keep-candidate-on-failure",
        action="store_true",
        help="Keep candidate artifact even if quality gate fails.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite candidate artifact if it already exists.",
    )

    args = parser.parse_args(argv)
    if args.max_docs_per_tag <= 0:
        parser.error("--max-docs-per-tag must be > 0")
    if args.head_character_n <= 0:
        parser.error("--head-character-n must be > 0")
    if not (0.05 <= args.validation_size <= 0.5):
        parser.error("--validation-size must be between 0.05 and 0.5")
    if args.max_workers <= 0:
        parser.error("--max-workers must be > 0")
    if not args.positive_tags:
        parser.error("--positive-tags must not be empty")
    if not args.negative_tags:
        parser.error("--negative-tags must not be empty")
    return args


def ensure_tag_downloaded(tag: str) -> Path:
    from lexnlp.ml.catalog import get_path_from_catalog
    from lexnlp.ml.catalog.download import download_github_release

    try:
        return get_path_from_catalog(tag)
    except FileNotFoundError:
        download_github_release(tag, prompt_user=False)
        return get_path_from_catalog(tag)


def patch_legacy_estimator_attributes(pipeline: Pipeline) -> None:
    estimator = pipeline._final_estimator
    if hasattr(estimator, "sigma_"):
        if not hasattr(estimator, "var_"):
            estimator.var_ = estimator.sigma_
        if not hasattr(estimator, "variance_"):
            estimator.variance_ = estimator.var_

    for _, _, transform in pipeline._iter(with_final=False):
        transform.clip = hasattr(transform, "clip") and transform.clip


def load_pipeline_for_tag(tag: str) -> Tuple[Path, Pipeline]:
    path = ensure_tag_downloaded(tag)
    with path.open("rb") as model_file:
        pipeline = load(model_file)
    patch_legacy_estimator_attributes(pipeline)
    return path, pipeline


def iter_texts_from_archive(path: Path, *, max_docs: int, head_character_n: int) -> Iterable[str]:
    yielded = 0
    with tarfile.open(path, mode="r:*") as archive:
        for member in archive:
            if yielded >= max_docs:
                break
            if not member.isfile() or not member.name.lower().endswith(".txt"):
                continue
            file_obj = archive.extractfile(member)
            if file_obj is None:
                continue
            payload = file_obj.read(head_character_n * 2)
            text = payload.decode("utf-8", errors="ignore").strip()
            if not text:
                continue
            yield text[:head_character_n]
            yielded += 1


def collect_corpus_samples(
    tags: Iterable[str],
    *,
    label: bool,
    max_docs_per_tag: int,
    head_character_n: int,
) -> Tuple[List[str], List[bool], Dict[str, int]]:
    texts: List[str] = []
    labels: List[bool] = []
    counts: Dict[str, int] = {}

    for tag in tags:
        archive_path = ensure_tag_downloaded(tag)
        extracted = list(
            iter_texts_from_archive(
                archive_path,
                max_docs=max_docs_per_tag,
                head_character_n=head_character_n,
            )
        )
        if not extracted:
            raise TrainingError(f"No text samples extracted from {tag} ({archive_path})")
        texts.extend(extracted)
        labels.extend([label] * len(extracted))
        counts[tag] = len(extracted)
    return texts, labels, counts


def make_estimator(name: str, *, random_state: int, max_workers: int):
    if name == "gaussian_nb":
        return GaussianNB()
    if name == "logistic_regression":
        return LogisticRegression(
            class_weight="balanced",
            max_iter=600,
            random_state=random_state,
        )
    if name == "random_forest":
        return RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced_subsample",
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=max_workers,
        )
    raise ValueError(f"Unsupported estimator: {name}")


def build_candidate_pipeline(feature_steps: Sequence[Tuple[str, object]], estimator_name: str, *, random_state: int, max_workers: int) -> Pipeline:
    steps = [(name, copy.deepcopy(step)) for name, step in feature_steps]
    steps.append((estimator_name, make_estimator(estimator_name, random_state=random_state, max_workers=max_workers)))
    return Pipeline(steps=steps)


def score_pipeline(
    pipeline: Pipeline,
    texts: Sequence[str],
    labels: Sequence[bool],
    *,
    min_probability: float,
) -> Dict[str, float]:
    probabilities = pipeline.predict_proba(texts)[:, 1]
    predictions = probabilities >= min_probability
    return {
        "accuracy": float(accuracy_score(labels, predictions)),
        "f1": float(f1_score(labels, predictions)),
        "precision": float(precision_score(labels, predictions, zero_division=0)),
        "recall": float(recall_score(labels, predictions, zero_division=0)),
    }


def choose_best(scores: Mapping[str, Dict[str, float]]) -> str:
    ranked = sorted(
        scores.items(),
        key=lambda item: (
            item[1]["f1"],
            item[1]["accuracy"],
            item[1]["precision"],
            item[1]["recall"],
        ),
        reverse=True,
    )
    return ranked[0][0]


def write_candidate_to_catalog(
    *,
    baseline_model_path: Path,
    candidate_tag: str,
    pipeline: Pipeline,
    force: bool,
) -> Path:
    from lexnlp.ml.catalog import CATALOG

    destination_dir = CATALOG / candidate_tag
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination_path = destination_dir / baseline_model_path.name

    if destination_path.exists() and not force:
        raise FileExistsError(
            f"Candidate path already exists: {destination_path}. Pass --force to overwrite."
        )

    with destination_path.open("wb") as candidate_file:
        pickle.dump(pipeline, candidate_file)
    return destination_path


def run_quality_gate(
    *,
    baseline_tag: str,
    candidate_tag: str,
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
        baseline_tag,
        "--candidate-tag",
        candidate_tag,
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


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)

    baseline_model_path, baseline_pipeline = load_pipeline_for_tag(args.baseline_tag)
    feature_steps = baseline_pipeline.steps[:-1]
    if not feature_steps:
        raise TrainingError("Baseline pipeline has no feature steps to reuse.")

    positive_texts, positive_labels, positive_counts = collect_corpus_samples(
        args.positive_tags,
        label=True,
        max_docs_per_tag=args.max_docs_per_tag,
        head_character_n=args.head_character_n,
    )
    negative_texts, negative_labels, negative_counts = collect_corpus_samples(
        args.negative_tags,
        label=False,
        max_docs_per_tag=args.max_docs_per_tag,
        head_character_n=args.head_character_n,
    )

    texts = positive_texts + negative_texts
    labels = positive_labels + negative_labels

    X_train, X_val, y_train, y_val = train_test_split(
        texts,
        labels,
        test_size=args.validation_size,
        random_state=args.random_state,
        shuffle=True,
        stratify=labels,
    )

    estimator_scores: Dict[str, Dict[str, float]] = {}
    fitted_pipelines: Dict[str, Pipeline] = {}
    for estimator_name in args.estimators:
        candidate = build_candidate_pipeline(
            feature_steps,
            estimator_name,
            random_state=args.random_state,
            max_workers=args.max_workers,
        )
        candidate.fit(X_train, y_train)
        patch_legacy_estimator_attributes(candidate)
        estimator_scores[estimator_name] = score_pipeline(
            candidate,
            X_val,
            y_val,
            min_probability=args.min_probability,
        )
        fitted_pipelines[estimator_name] = candidate

    selected_estimator = choose_best(estimator_scores)

    # Refit the selected estimator on the full dataset before writing candidate.
    selected_pipeline = build_candidate_pipeline(
        feature_steps,
        selected_estimator,
        random_state=args.random_state,
        max_workers=args.max_workers,
    )
    selected_pipeline.fit(texts, labels)
    patch_legacy_estimator_attributes(selected_pipeline)

    candidate_model_path = write_candidate_to_catalog(
        baseline_model_path=baseline_model_path,
        candidate_tag=args.candidate_tag,
        pipeline=selected_pipeline,
        force=args.force,
    )

    report = {
        "baseline_tag": args.baseline_tag,
        "candidate_tag": args.candidate_tag,
        "baseline_model_path": str(baseline_model_path),
        "candidate_model_path": str(candidate_model_path),
        "selected_estimator": selected_estimator,
        "estimators": estimator_scores,
        "dataset": {
            "positive_counts": positive_counts,
            "negative_counts": negative_counts,
            "total_samples": len(texts),
            "train_samples": len(X_train),
            "validation_samples": len(X_val),
            "max_docs_per_tag": args.max_docs_per_tag,
            "head_character_n": args.head_character_n,
        },
        "validation_baseline": score_pipeline(
            baseline_pipeline,
            X_val,
            y_val,
            min_probability=args.min_probability,
        ),
        "validation_candidate_selected": score_pipeline(
            selected_pipeline,
            X_val,
            y_val,
            min_probability=args.min_probability,
        ),
        "quality_gate": {
            "skipped": bool(args.skip_quality_gate),
            "status": "not-run" if args.skip_quality_gate else "pending",
        },
    }

    if args.skip_quality_gate:
        report["quality_gate"]["status"] = "skipped"
    else:
        try:
            run_quality_gate(
                baseline_tag=args.baseline_tag,
                candidate_tag=args.candidate_tag,
                fixture=args.fixture,
                baseline_metrics_json=args.baseline_metrics_json,
                min_probability=args.min_probability,
                max_accuracy_regression=args.max_accuracy_regression,
                max_f1_regression=args.max_f1_regression,
            )
            report["quality_gate"]["status"] = "passed"
        except subprocess.CalledProcessError:
            report["quality_gate"]["status"] = "failed"
            if not args.keep_candidate_on_failure and candidate_model_path.exists():
                candidate_model_path.unlink()
                report["quality_gate"]["candidate_removed"] = True
            args.output_json.parent.mkdir(parents=True, exist_ok=True)
            args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
            return 1

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
