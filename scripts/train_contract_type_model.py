#!/usr/bin/env python3
"""Train and store a runtime-compatible contract-type classifier."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, Sequence

from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

from lexnlp.extract.en.contracts.runtime_model import (
    CONTRACT_TYPE_CORPUS_TAG,
    RUNTIME_CONTRACT_TYPE_TAG,
    collect_contract_type_samples,
    ensure_tag_downloaded,
    train_contract_type_pipeline,
    write_pipeline_to_catalog,
)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Train a contract-type classifier from LexNLP corpus assets and write "
            "it into the local LexNLP catalog."
        )
    )
    parser.add_argument(
        "--target-tag",
        default=RUNTIME_CONTRACT_TYPE_TAG,
        help=f"Catalog tag to write (default: {RUNTIME_CONTRACT_TYPE_TAG}).",
    )
    parser.add_argument(
        "--corpus-tag",
        default=CONTRACT_TYPE_CORPUS_TAG,
        help=f"Corpus tag to read training examples from (default: {CONTRACT_TYPE_CORPUS_TAG}).",
    )
    parser.add_argument(
        "--max-docs-per-label",
        type=int,
        default=120,
        help="Maximum sampled documents per label.",
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
        help="Validation split ratio.",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=7,
        help="Random seed for split/training.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing target model if it exists.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("artifacts/model_training/contract_type_model_training_report.json"),
        help="Path to write training summary JSON.",
    )
    return parser.parse_args(argv)


def score(labels, predictions) -> Dict[str, float]:
    return {
        "accuracy": float(accuracy_score(labels, predictions)),
        "f1_macro": float(f1_score(labels, predictions, average="macro")),
        "f1_weighted": float(f1_score(labels, predictions, average="weighted")),
    }


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)

    corpus_archive = ensure_tag_downloaded(args.corpus_tag)
    texts, labels, counts = collect_contract_type_samples(
        corpus_archive,
        max_docs_per_label=args.max_docs_per_label,
        head_character_n=args.head_character_n,
    )

    label_counts = Counter(labels)
    can_stratify = min(label_counts.values()) >= 2

    x_train, x_val, y_train, y_val = train_test_split(
        texts,
        labels,
        test_size=args.validation_size,
        random_state=args.random_state,
        stratify=labels if can_stratify else None,
        shuffle=True,
    )

    validation_pipeline = train_contract_type_pipeline(
        x_train,
        y_train,
        random_state=args.random_state,
    )
    validation_predictions = validation_pipeline.predict(x_val)
    validation_metrics = score(y_val, validation_predictions)

    final_pipeline = train_contract_type_pipeline(
        texts,
        labels,
        random_state=args.random_state,
    )
    destination = write_pipeline_to_catalog(
        pipeline=final_pipeline,
        target_tag=args.target_tag,
        force=args.force,
    )

    report = {
        "target_tag": args.target_tag,
        "target_model_path": str(destination),
        "corpus_tag": args.corpus_tag,
        "corpus_path": str(corpus_archive),
        "dataset": {
            "labels": len(counts),
            "samples_total": len(texts),
            "samples_train": len(x_train),
            "samples_validation": len(x_val),
            "stratified_split": can_stratify,
            "min_samples_per_label": min(label_counts.values()),
            "max_docs_per_label": args.max_docs_per_label,
            "head_character_n": args.head_character_n,
        },
        "validation_metrics": validation_metrics,
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
