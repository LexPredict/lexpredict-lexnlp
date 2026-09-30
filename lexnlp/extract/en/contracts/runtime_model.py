"""
Utilities to build and load a Python 3.11-compatible contract-type classifier.
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# standard library
import logging
import pickle
import tarfile
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

# third-party imports
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from threadpoolctl import threadpool_limits
from requests import RequestException

from lexnlp.ml.artifact_io import atomic_output_path
from lexnlp.utils.unpickler import load_sklearn_model


LOGGER = logging.getLogger(__name__)

LEGACY_CONTRACT_TYPE_TAG = "pipeline/contract-type/0.1"
RUNTIME_CONTRACT_TYPE_TAG = "pipeline/contract-type/0.2-runtime"
CONTRACT_TYPE_CORPUS_TAG = "corpus/contract-types/0.1"
CONTRACT_TYPE_MODEL_FILENAME = "pipeline_contract_type_classifier.cloudpickle"
CONTRACT_TYPE_TRAINING_THREADS = 1


def ensure_tag_downloaded(tag: str) -> Path:
    from lexnlp.ml.catalog import get_exact_path_from_catalog
    from lexnlp.ml.catalog.download import (
        download_github_release_to_path,
        load_asset_manifest,
        verify_trusted_asset_file,
    )

    manifest = load_asset_manifest()
    trusted = manifest.assets.get(tag)
    try:
        path = get_exact_path_from_catalog(tag)
    except FileNotFoundError:
        LOGGER.info("Catalog tag missing; downloading release tag=%s", tag)
        return download_github_release_to_path(tag)

    if trusted is not None:
        verify_trusted_asset_file(path, tag)
    return path


def load_pipeline_for_tag(tag: str) -> Pipeline:
    from lexnlp.ml.catalog import get_exact_path_from_catalog, get_path_from_catalog
    from lexnlp.ml.catalog.download import load_asset_manifest, verify_trusted_asset_file

    try:
        path = get_path_from_catalog(tag)
    except FileNotFoundError:
        path = ensure_tag_downloaded(tag)
    else:
        try:
            exact_path = get_exact_path_from_catalog(tag)
        except FileNotFoundError:
            # ``get_path_from_catalog`` may intentionally resolve a private
            # local candidate for a missing release tag.
            pass
        else:
            if exact_path == path and tag in load_asset_manifest().assets:
                verify_trusted_asset_file(path, tag)
    with path.open("rb") as model_file:
        return load_sklearn_model(model_file)


def _extract_label(member_name: str) -> str:
    # Expected shape: CONTRACT_TYPES/<LABEL>/<filename>.txt
    parts: Sequence[str] = Path(member_name).parts
    if len(parts) < 3:
        raise ValueError(f"Unexpected corpus member path: {member_name}")
    return parts[-2]


def collect_contract_type_samples(
    archive_path: Path,
    *,
    max_docs_per_label: int,
    head_character_n: int,
) -> Tuple[List[str], List[str], Dict[str, int]]:
    if max_docs_per_label < 0:
        raise ValueError("max_docs_per_label must be >= 0")
    if head_character_n <= 0:
        raise ValueError("head_character_n must be > 0")

    texts: List[str] = []
    labels: List[str] = []
    counts: Dict[str, int] = defaultdict(int)

    with tarfile.open(archive_path, mode="r:*") as archive:
        # The corpus release is integrity-pinned, including its member order.
        # Preserve that canonical order because the per-label cap makes order
        # part of the published training recipe.
        members: Iterable[tarfile.TarInfo] = archive
        for member in members:
            if not member.isfile() or not member.name.lower().endswith(".txt"):
                continue

            label = _extract_label(member.name)
            if max_docs_per_label and counts[label] >= max_docs_per_label:
                continue

            file_obj = archive.extractfile(member)
            if file_obj is None:
                continue
            payload = file_obj.read(head_character_n * 2)
            text = payload.decode("utf-8", errors="ignore").strip()
            if not text:
                continue

            texts.append(text[:head_character_n])
            labels.append(label)
            counts[label] += 1

    if not texts:
        raise RuntimeError(f"No samples collected from {archive_path}")
    if len(set(labels)) < 2:
        raise RuntimeError(
            "Contract-type training requires at least two labels; "
            f"found {len(set(labels))}"
        )

    return texts, labels, dict(counts)


def train_contract_type_pipeline(
    texts: Sequence[str],
    labels: Sequence[str],
    *,
    random_state: int,
    max_features: int = 75_000,
) -> Pipeline:
    if len(texts) != len(labels):
        raise ValueError("texts and labels length mismatch")
    if max_features <= 0:
        raise ValueError("max_features must be > 0")

    pipeline = Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    strip_accents="unicode",
                    ngram_range=(1, 2),
                    min_df=2,
                    max_features=max_features,
                    sublinear_tf=True,
                ),
            ),
            (
                "logistic_regression",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=1000,
                    random_state=random_state,
                    solver="lbfgs",
                ),
            ),
        ]
    )
    # BLAS reductions can differ at the last few floating-point bits when their
    # work is scheduled across a variable number of threads.  A fixed
    # single-thread fit makes release artifacts byte-reproducible and also
    # prevents runtime fallback training from oversubscribing small hosts.
    with threadpool_limits(limits=CONTRACT_TYPE_TRAINING_THREADS):
        pipeline.fit(texts, labels)
    return pipeline


def write_pipeline_to_catalog(
    *,
    pipeline: Pipeline,
    target_tag: str,
    force: bool,
) -> Path:
    from lexnlp.ml.catalog import get_catalog_directory, invalidate_catalog_cache
    from lexnlp.ml.catalog.download import (
        AssetTrustError,
        load_asset_manifest,
        verify_trusted_asset_file,
        verify_trusted_asset_payload,
    )

    destination_dir = get_catalog_directory(target_tag)
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination_path = destination_dir / CONTRACT_TYPE_MODEL_FILENAME
    manifest = load_asset_manifest()
    trusted_target = manifest.assets.get(target_tag)

    if destination_path.exists() and not force:
        try:
            if trusted_target is not None:
                verify_trusted_asset_file(destination_path, target_tag)
            with destination_path.open("rb") as model_file:
                load_sklearn_model(model_file)
            return destination_path
        except AssetTrustError:
            raise
        except Exception:
            LOGGER.warning(
                "Existing contract-type model is invalid; replacing it: %s",
                destination_path,
                exc_info=True,
            )

    with atomic_output_path(destination_path) as temporary_path:
        with temporary_path.open("wb") as model_file:
            pickle.dump(pipeline, model_file)
        with temporary_path.open("rb") as model_file:
            load_sklearn_model(model_file)
        if trusted_target is not None:
            # A manifest-pinned release tag may only contain the exact reviewed
            # bytes.  Locally trained runtime candidates use a private tag.
            verify_trusted_asset_payload(temporary_path, target_tag)
    invalidate_catalog_cache()
    return destination_path


def ensure_runtime_contract_type_model(
    *,
    target_tag: str = RUNTIME_CONTRACT_TYPE_TAG,
    force: bool = False,
    max_docs_per_label: int = 0,
    head_character_n: int = 4000,
    random_state: int = 7,
    max_features: int = 75_000,
) -> Path:
    from lexnlp.ml.catalog import (
        get_exact_path_from_catalog,
        get_local_candidate_tag,
    )
    from lexnlp.ml.catalog.download import (
        AssetTrustError,
        download_github_release_to_path,
        load_asset_manifest,
        verify_trusted_asset_file,
    )

    manifest = load_asset_manifest()
    trusted_release = target_tag in manifest.assets
    local_target_tag = (
        get_local_candidate_tag(target_tag)
        if trusted_release
        else target_tag
    )

    if trusted_release:
        try:
            release_path = get_exact_path_from_catalog(target_tag)
        except FileNotFoundError:
            pass
        else:
            # Never turn a checksum/trust failure into a training fallback.
            verify_trusted_asset_file(release_path, target_tag)
            if not force:
                with release_path.open("rb") as model_file:
                    load_sklearn_model(model_file)
                return release_path

    if not force:
        try:
            local_path = get_exact_path_from_catalog(local_target_tag)
        except FileNotFoundError:
            pass
        else:
            try:
                with local_path.open("rb") as model_file:
                    load_sklearn_model(model_file)
                return local_path
            except Exception:
                LOGGER.warning(
                    "Existing local contract-type candidate is invalid; rebuilding it: %s",
                    local_path,
                    exc_info=True,
                )

    if trusted_release and not force:
        # Prefer downloading a published runtime-compatible artifact when
        # available to avoid retraining in CI environments.
        try:
            downloaded_path = download_github_release_to_path(target_tag)
        except AssetTrustError:
            raise
        except RequestException as exc:
            LOGGER.warning(
                "Unable to download runtime contract-type release tag=%s; "
                "building private local candidate instead. error=%s",
                target_tag,
                exc,
            )
        else:
            with downloaded_path.open("rb") as model_file:
                load_sklearn_model(model_file)
            return downloaded_path

    corpus_archive = ensure_tag_downloaded(CONTRACT_TYPE_CORPUS_TAG)
    texts, labels, _counts = collect_contract_type_samples(
        corpus_archive,
        max_docs_per_label=max_docs_per_label,
        head_character_n=head_character_n,
    )
    pipeline = train_contract_type_pipeline(
        texts,
        labels,
        random_state=random_state,
        max_features=max_features,
    )
    destination_path = write_pipeline_to_catalog(
        pipeline=pipeline,
        target_tag=local_target_tag,
        force=True,
    )
    LOGGER.info(
        "Trained local runtime contract-type candidate release_tag=%s local_tag=%s at %s",
        target_tag,
        local_target_tag,
        destination_path,
    )
    return destination_path
