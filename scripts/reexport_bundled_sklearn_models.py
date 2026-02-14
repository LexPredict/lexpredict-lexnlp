#!/usr/bin/env python3
"""Re-export bundled sklearn/joblib artifacts to match the current runtime.

This reduces legacy scikit-learn unpickle warnings and removes reliance on
compatibility shims for old module paths.
"""

from __future__ import annotations

import argparse
import io
import pickle
import warnings
from pathlib import Path
from typing import Iterable, Sequence
from zipfile import ZipFile, ZIP_STORED

import joblib


BUNDLED_MODEL_PATHS: tuple[Path, ...] = (
    Path("lexnlp/extract/de/date_model.pickle"),
    Path("lexnlp/extract/de/model.pickle"),
    Path("lexnlp/extract/en/addresses/addresses_clf.pickle"),
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
    return parser.parse_args(argv)


def iter_paths(args: argparse.Namespace) -> Iterable[Path]:
    if args.paths:
        for raw in args.paths:
            yield Path(raw)
    else:
        yield from BUNDLED_MODEL_PATHS


def load_model(path: Path):
    # Most artifacts are joblib dumps; the address classifier is loaded via
    # RenameUnpickler for legacy sklearn module paths.
    if path.name == "addresses_clf.pickle":
        from lexnlp.utils.unpickler import renamed_load

        with path.open("rb") as f:
            try:
                return renamed_load(f)
            except Exception:
                # If the file was previously dumped with joblib, fall back so we
                # can re-export it into a plain pickle again.
                return joblib.load(path)
    return joblib.load(path)


def load_layered_definition_models(path: Path):
    from lexnlp.utils.unpickler import renamed_load

    with ZipFile(path) as archive:
        payload = {}
        for name in ("term.pickle", "definition.pickle"):
            raw = archive.read(name)
            payload[name] = renamed_load(io.BytesIO(raw))
    return payload


def reexport_layered_definition_models(path: Path) -> None:
    payload = load_layered_definition_models(path)
    tmp_path = path.with_name(path.name + ".part")
    if tmp_path.exists():
        tmp_path.unlink()

    with ZipFile(tmp_path, mode="w", compression=ZIP_STORED) as archive:
        for name in ("term.pickle", "definition.pickle"):
            archive.writestr(
                name,
                pickle.dumps(payload[name], protocol=pickle.HIGHEST_PROTOCOL),
            )
    tmp_path.replace(path)


def legacy_warning_count_for_load(path: Path) -> int:
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        if path.name == "definition_model_layered.pickle.gzip":
            _ = load_layered_definition_models(path)
        else:
            _ = load_model(path)
    return sum(1 for item in captured if LEGACY_WARNING_TOKEN in str(item.message))


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    failures: list[str] = []

    for path in iter_paths(args):
        if not path.exists():
            failures.append(f"missing: {path}")
            continue

        before = legacy_warning_count_for_load(path)

        if path.name == "definition_model_layered.pickle.gzip":
            reexport_layered_definition_models(path)
        else:
            model = load_model(path)
            if path.name == "addresses_clf.pickle":
                # Keep as a plain pickle so lexnlp.extract.en.addresses.addresses
                # can keep using RenameUnpickler for old module-path compatibility.
                with path.open("wb") as f:
                    pickle.dump(model, f, protocol=pickle.HIGHEST_PROTOCOL)
            else:
                joblib.dump(model, path, compress=args.compress)

        after = legacy_warning_count_for_load(path)
        print(f"reexport: {path} legacy_warnings before={before} after={after}")

    if failures:
        for failure in failures:
            print(f"reexport: ERROR {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__('sys').argv[1:]))
