#!/usr/bin/env python3
"""Deterministic cross-platform bootstrap utility for LexNLP assets."""

from __future__ import annotations

import argparse
import logging
import os
import sys
import zipfile
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple
from urllib.request import Request, urlopen

LOGGER = logging.getLogger("lexnlp.bootstrap")

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STANFORD_DIR = REPO_ROOT / "libs" / "stanford_nlp"
DEFAULT_TIKA_DIR = REPO_ROOT / "bin"

NLTK_RESOURCES = (
    "punkt",
    "wordnet",
    "omw-1.4",
    "averaged_perceptron_tagger",
    "maxent_ne_chunker",
    "words",
)
OPTIONAL_NLTK_RESOURCES = ("punkt_tab",)


def resolve_contract_model_tag() -> str:
    """
    Resolve the contract-model tag from env overrides with backward compatibility.
    """
    return (
        os.getenv("LEXNLP_CONTRACT_MODEL_TAG")
        or os.getenv("LEXNLP_IS_CONTRACT_MODEL_TAG")
        or "pipeline/is-contract/0.2"
    ).strip()


def resolve_contract_type_model_tag() -> str:
    """
    Resolve the contract-type model tag from env overrides.
    """
    return (
        os.getenv("LEXNLP_CONTRACT_TYPE_MODEL_TAG")
        or "pipeline/contract-type/0.2-runtime"
    ).strip()


CONTRACT_MODEL_TAG = resolve_contract_model_tag()

STANFORD_DOWNLOADS: Tuple[Tuple[str, str, Tuple[str, ...]], ...] = (
    (
        "stanford-postagger-full-2017-06-09.zip",
        "https://nlp.stanford.edu/software/stanford-postagger-full-2017-06-09.zip",
        (
            "stanford-postagger-full-2017-06-09/stanford-postagger.jar",
            "stanford-postagger-full-2017-06-09/models/english-bidirectional-distsim.tagger",
        ),
    ),
    (
        "stanford-ner-2017-06-09.zip",
        "https://nlp.stanford.edu/software/stanford-ner-2017-06-09.zip",
        (
            "stanford-ner-2017-06-09/stanford-ner.jar",
            "stanford-ner-2017-06-09/classifiers/english.all.3class.distsim.crf.ser.gz",
        ),
    ),
)

TIKA_DOWNLOADS: Tuple[Tuple[str, str], ...] = (
    (
        "tika-app-1.16.jar",
        "https://archive.apache.org/dist/tika/tika-app-1.16.jar",
    ),
    (
        "tika-server-1.16.jar",
        "https://archive.apache.org/dist/tika/tika-server-1.16.jar",
    ),
)


class BootstrapError(Exception):
    """Raised when one or more bootstrap tasks fail."""


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="[bootstrap][%(levelname)s] %(message)s")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap LexNLP runtime/test assets in a deterministic way.",
    )
    parser.add_argument("--nltk", action="store_true", help="Download required NLTK resources.")
    parser.add_argument(
        "--contract-model",
        action="store_true",
        help=(
            "Download LexNLP contract model release. "
            "Respects env overrides LEXNLP_CONTRACT_MODEL_TAG / "
            "LEXNLP_IS_CONTRACT_MODEL_TAG."
        ),
    )
    parser.add_argument(
        "--contract-type-model",
        action="store_true",
        help=(
            "Build or reuse a Python-runtime-compatible contract-type model "
            "from corpora. Respects LEXNLP_CONTRACT_TYPE_MODEL_TAG."
        ),
    )
    parser.add_argument(
        "--stanford",
        action="store_true",
        help="Download Stanford POS tagger and NER ZIP artifacts.",
    )
    parser.add_argument(
        "--tika",
        action="store_true",
        help="Download Apache Tika 1.16 app/server jars.",
    )
    parser.add_argument("--all", action="store_true", help="Run all bootstrap tasks.")
    parser.add_argument(
        "--stanford-dir",
        default=str(DEFAULT_STANFORD_DIR),
        help="Destination directory for Stanford ZIPs (default: libs/stanford_nlp).",
    )
    parser.add_argument(
        "--tika-dir",
        default=str(DEFAULT_TIKA_DIR),
        help="Destination directory for Tika jars (default: bin).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned actions without network/file writes.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download files even if destination files already exist.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Network timeout in seconds for each request (default: 60).",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")

    args = parser.parse_args(argv)

    if not any(
        (
            args.nltk,
            args.contract_model,
            args.contract_type_model,
            args.stanford,
            args.tika,
            args.all,
        )
    ):
        parser.error(
            "Select at least one task: --nltk, --contract-model, --contract-type-model, "
            "--stanford, --tika, or --all"
        )

    if args.timeout <= 0:
        parser.error("--timeout must be a positive integer")

    return args


def ensure_directory(path: Path, dry_run: bool) -> None:
    if dry_run:
        LOGGER.info("DRY RUN: would create directory %s", path)
        return
    path.mkdir(parents=True, exist_ok=True)


def download_file(
    url: str,
    destination: Path,
    *,
    force: bool,
    dry_run: bool,
    timeout: int,
) -> None:
    if destination.exists() and not force:
        LOGGER.info("Skipping existing file: %s", destination)
        return

    ensure_directory(destination.parent, dry_run=dry_run)

    if dry_run:
        LOGGER.info("DRY RUN: would download %s -> %s", url, destination)
        return

    tmp_destination = destination.with_name(destination.name + ".part")
    if tmp_destination.exists():
        tmp_destination.unlink()

    request = Request(url, headers={"User-Agent": "lexnlp-bootstrap/1.0"})
    LOGGER.info("Downloading %s", url)

    try:
        with urlopen(request, timeout=timeout) as response, tmp_destination.open("wb") as output_file:
            while True:
                chunk = response.read(64 * 1024)
                if not chunk:
                    break
                output_file.write(chunk)
        tmp_destination.replace(destination)
    except Exception:
        if tmp_destination.exists():
            tmp_destination.unlink()
        raise

    LOGGER.info("Saved %s", destination)


def download_many(
    downloads: Iterable[Tuple[str, str]],
    destination_dir: Path,
    *,
    force: bool,
    dry_run: bool,
    timeout: int,
) -> None:
    for filename, url in downloads:
        destination = destination_dir / filename
        download_file(url, destination, force=force, dry_run=dry_run, timeout=timeout)


def extract_zip(archive_path: Path, destination_dir: Path, *, dry_run: bool) -> None:
    if dry_run:
        LOGGER.info("DRY RUN: would extract %s -> %s", archive_path, destination_dir)
        return
    LOGGER.info("Extracting %s", archive_path)
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(destination_dir)


def bootstrap_stanford_assets(
    destination_dir: Path,
    *,
    force: bool,
    dry_run: bool,
    timeout: int,
) -> None:
    ensure_directory(destination_dir, dry_run=dry_run)
    for filename, url, required_files in STANFORD_DOWNLOADS:
        required_paths = [destination_dir / rel_path for rel_path in required_files]
        if all(path.exists() for path in required_paths) and not force:
            LOGGER.info("Skipping Stanford asset already present: %s", filename)
            continue

        archive_path = destination_dir / filename
        download_file(url, archive_path, force=force, dry_run=dry_run, timeout=timeout)
        extract_zip(archive_path, destination_dir, dry_run=dry_run)

    if dry_run:
        return

    missing = []
    for _, _, required_files in STANFORD_DOWNLOADS:
        for required_file in required_files:
            candidate = destination_dir / required_file
            if not candidate.exists():
                missing.append(candidate)
    if missing:
        missing_display = ", ".join(str(path) for path in missing)
        raise RuntimeError(f"Missing required Stanford files after download: {missing_display}")


def bootstrap_nltk(*, dry_run: bool) -> None:
    if dry_run:
        for resource in NLTK_RESOURCES:
            LOGGER.info("DRY RUN: would download NLTK resource %s", resource)
        return

    try:
        import nltk
    except ImportError as error:
        raise RuntimeError("nltk is required for --nltk. Install dependencies first.") from error

    for resource in NLTK_RESOURCES:
        LOGGER.info("Downloading NLTK resource: %s", resource)
        nltk.download(resource, quiet=True, raise_on_error=True)

    for resource in OPTIONAL_NLTK_RESOURCES:
        LOGGER.info("Attempting optional NLTK resource: %s", resource)
        try:
            nltk.download(resource, quiet=True, raise_on_error=True)
        except Exception:
            LOGGER.warning("Optional NLTK resource unavailable: %s", resource)


def bootstrap_contract_model(*, dry_run: bool, tag: str) -> None:
    if dry_run:
        LOGGER.info("DRY RUN: would download LexNLP model tag %s", tag)
        return

    try:
        from lexnlp.ml.catalog.download import download_github_release
    except ImportError as error:
        raise RuntimeError(
            "Unable to import LexNLP catalog downloader. Ensure dependencies and editable install are in place."
        ) from error

    LOGGER.info("Downloading LexNLP contract model: %s", tag)
    try:
        download_github_release(tag, prompt_user=False)
        return
    except Exception as exc:
        # The default tag may not exist yet in the configured models repo.
        # Only fall back when the tag was not explicitly set by the user.
        explicit = bool(
            (os.getenv("LEXNLP_CONTRACT_MODEL_TAG") or "").strip()
            or (os.getenv("LEXNLP_IS_CONTRACT_MODEL_TAG") or "").strip()
        )
        status_code = getattr(getattr(exc, "response", None), "status_code", None)
        legacy_tag = "pipeline/is-contract/0.1"

        if not explicit and tag == "pipeline/is-contract/0.2" and status_code == 404:
            LOGGER.warning(
                "Contract model tag=%s not found (HTTP 404); bootstrapping legacy tag=%s and generating runtime tag=%s",
                tag,
                legacy_tag,
                tag,
            )

            # Ensure the baseline tag is available locally.
            download_github_release(legacy_tag, prompt_user=False)

            # Re-export legacy artifact into the requested tag so modern defaults
            # work even before a Release asset exists for `pipeline/is-contract/0.2`.
            try:
                from cloudpickle import load

                from lexnlp.extract.en.contracts.predictors import ProbabilityPredictorIsContract
                from lexnlp.ml.catalog import CATALOG, get_path_from_catalog

                source_path = get_path_from_catalog(legacy_tag)
                destination_dir = CATALOG / tag
                destination_path = destination_dir / source_path.name
                destination_dir.mkdir(parents=True, exist_ok=True)

                with source_path.open("rb") as source_file:
                    pipeline = load(source_file)

                # Validate and apply runtime compatibility patches before dumping.
                ProbabilityPredictorIsContract(pipeline=pipeline)

                import pickle

                with destination_path.open("wb") as destination_file:
                    pickle.dump(pipeline, destination_file, protocol=pickle.HIGHEST_PROTOCOL)

                LOGGER.info("Generated contract model tag=%s at %s", tag, destination_path)
            except Exception:
                LOGGER.exception(
                    "Failed to generate contract model tag=%s from legacy tag=%s; continuing with legacy only",
                    tag,
                    legacy_tag,
                )
            return
        raise


def bootstrap_contract_type_model(*, dry_run: bool, tag: str) -> None:
    if dry_run:
        LOGGER.info(
            "DRY RUN: would build/reuse runtime-compatible contract-type model tag %s",
            tag,
        )
        return

    try:
        from lexnlp.extract.en.contracts.runtime_model import ensure_runtime_contract_type_model
    except ImportError as error:
        raise RuntimeError(
            "Unable to import contract-type runtime model builder. "
            "Ensure dependencies and editable install are in place."
        ) from error

    LOGGER.info("Ensuring runtime-compatible contract-type model: %s", tag)
    ensure_runtime_contract_type_model(target_tag=tag)


def run_selected_tasks(args: argparse.Namespace) -> None:
    run_nltk = args.all or args.nltk
    run_contract_model = args.all or args.contract_model
    run_contract_type_model = args.all or args.contract_type_model
    run_stanford = args.all or args.stanford
    run_tika = args.all or args.tika

    tasks: List[Tuple[str, object]] = []
    if run_nltk:
        tasks.append(("nltk", lambda: bootstrap_nltk(dry_run=args.dry_run)))
    if run_contract_model:
        contract_model_tag = resolve_contract_model_tag()
        tasks.append(
            (
                "contract-model",
                lambda: bootstrap_contract_model(
                    dry_run=args.dry_run,
                    tag=contract_model_tag,
                ),
            )
        )
    if run_contract_type_model:
        contract_type_model_tag = resolve_contract_type_model_tag()
        tasks.append(
            (
                "contract-type-model",
                lambda: bootstrap_contract_type_model(
                    dry_run=args.dry_run,
                    tag=contract_type_model_tag,
                ),
            )
        )
    if run_stanford:
        stanford_dir = Path(args.stanford_dir).expanduser().resolve()
        tasks.append(
            (
                "stanford",
                lambda: bootstrap_stanford_assets(
                    stanford_dir,
                    force=args.force,
                    dry_run=args.dry_run,
                    timeout=args.timeout,
                ),
            )
        )
    if run_tika:
        tika_dir = Path(args.tika_dir).expanduser().resolve()
        tasks.append(
            (
                "tika",
                lambda: download_many(
                    TIKA_DOWNLOADS,
                    tika_dir,
                    force=args.force,
                    dry_run=args.dry_run,
                    timeout=args.timeout,
                ),
            )
        )

    failures: List[str] = []
    for name, task in tasks:
        LOGGER.info("Starting task: %s", name)
        try:
            task()
            LOGGER.info("Finished task: %s", name)
        except Exception:
            LOGGER.exception("Task failed: %s", name)
            failures.append(name)

    if failures:
        raise BootstrapError("Failed tasks: {}".format(", ".join(failures)))


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    configure_logging(args.verbose)

    LOGGER.debug("Repository root: %s", REPO_ROOT)
    if args.dry_run:
        LOGGER.info("Dry-run mode enabled; no downloads or filesystem writes will occur.")

    try:
        run_selected_tasks(args)
    except BootstrapError as error:
        LOGGER.error(str(error))
        return 1

    LOGGER.info("Bootstrap tasks completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
