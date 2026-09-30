"""
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# standard library
import os
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath
from typing import Dict, Optional

# NLTK
import nltk.data


def _resolve_nltk_data_dir() -> Path:
    """
    Resolve a writable NLTK data directory for LexNLP assets.

    Historically LexNLP used ``nltk.data.find('')`` to discover the root of the
    NLTK data path. On fresh environments (e.g., CI runners), NLTK's internal
    implementation can raise when no candidate directories exist yet.

    This resolver prefers the first usable entry in ``nltk.data.path``. If none
    are usable, it falls back to ``~/nltk_data``.
    """
    candidates = [Path(p).expanduser() for p in nltk.data.path if p]
    candidates.append(Path.home() / "nltk_data")

    for candidate in candidates:
        if candidate.exists():
            if candidate.is_dir() and os.access(candidate, os.W_OK):
                return candidate
            continue

        # Candidate does not exist yet. Prefer a path whose nearest existing
        # parent is writable so downstream tasks can create directories.
        parent = candidate
        while not parent.exists() and parent.parent != parent:
            parent = parent.parent
        if parent.exists() and parent.is_dir() and os.access(parent, os.W_OK):
            return candidate

    # Last resort: current working directory.
    return Path.cwd() / "nltk_data"


def _resolve_catalog_dir() -> Path:
    """
    Resolve the LexNLP catalog directory where model/data assets live.

    This function does not create directories on import; callers that write into
    the catalog must create parent directories as needed.
    """
    root = _resolve_nltk_data_dir()
    return root / "lexpredict-lexnlp"


CATALOG: Path = _resolve_catalog_dir()
LOCAL_CANDIDATE_TAG_PREFIX = "_local-candidates"

_TAG_DICT_CACHE: Optional[Dict[str, Path]] = None


def _catalog_tag(path: PurePath, catalog: PurePath) -> str:
    """Return a platform-independent release tag for a catalog asset."""
    return path.parent.relative_to(catalog).as_posix()


def _build_tag_dict() -> Dict[str, Path]:
    """
    Builds a dictionary with the following structure:

    - keys (str): directory paths relative to CATALOG, each corresponding to GitHub release tags.
    - values (Path): file path under the directory ("tag").

    Returns:
        A dictionary.
    """
    return {
        _catalog_tag(path, CATALOG): path
        for path in CATALOG.rglob('*')
        if path.is_file()
    }


def invalidate_catalog_cache() -> None:
    """
    Clear the in-process catalog index.

    LexNLP downloads new tags at runtime. Most processes benefit from caching
    catalog lookups, but callers that add/remove assets can invalidate the cache
    explicitly (or rely on miss-based refresh in `get_path_from_catalog`).
    """
    global _TAG_DICT_CACHE
    _TAG_DICT_CACHE = None


def _get_tag_dict_cached() -> Dict[str, Path]:
    global _TAG_DICT_CACHE
    if _TAG_DICT_CACHE is None:
        _TAG_DICT_CACHE = _build_tag_dict()
    return _TAG_DICT_CACHE


def get_local_candidate_tag(tag: str) -> str:
    """Return the private catalog tag used for a locally built candidate.

    Local candidates deliberately live outside manifest-pinned release tags.
    ``get_path_from_catalog`` aliases a missing release tag to this private tag
    so existing predictors keep working without confusing local bytes with
    reviewed release bytes.
    """
    raw_tag = str(tag).strip()
    tag_path = PurePosixPath(raw_tag)
    windows_path = PureWindowsPath(raw_tag)
    if (
        not raw_tag
        or "\\" in raw_tag
        or tag_path.is_absolute()
        or windows_path.is_absolute()
        or bool(windows_path.drive)
        or bool(windows_path.root)
        or tag_path.as_posix() != raw_tag
        or any(part in ("", ".", "..") for part in raw_tag.split("/"))
    ):
        raise ValueError(f"Unsafe catalog tag: {tag!r}")
    return f"{LOCAL_CANDIDATE_TAG_PREFIX}/{raw_tag}"


def get_catalog_directory(tag: str) -> Path:
    """Return a contained catalog directory for a portable relative tag."""
    # Reuse candidate-tag validation, then discard the private prefix it adds.
    validated_tag = get_local_candidate_tag(tag).removeprefix(
        f"{LOCAL_CANDIDATE_TAG_PREFIX}/"
    )
    root = CATALOG.resolve()
    destination = (root / Path(*PurePosixPath(validated_tag).parts)).resolve()
    try:
        destination.relative_to(root)
    except ValueError as error:
        raise ValueError(f"Catalog tag escapes CATALOG: {tag!r}") from error
    return destination


def _find_exact_catalog_path(tag: str) -> Optional[Path]:
    """Find an exact catalog tag, refreshing the cache when necessary."""
    d: Dict[str, Path] = _get_tag_dict_cached()
    path: Optional[Path] = d.get(tag)

    # If a tag was downloaded after the cache was built, refresh on miss.
    if path is None:
        invalidate_catalog_cache()
        d = _get_tag_dict_cached()
        path = d.get(tag)

    # If the cached path was removed/overwritten, refresh once before failing.
    if path is not None and not path.exists():
        invalidate_catalog_cache()
        d = _get_tag_dict_cached()
        path = d.get(tag)
    return path


def get_exact_path_from_catalog(tag: str) -> Path:
    """Return only a file physically stored under the requested catalog tag."""
    path = _find_exact_catalog_path(tag)
    if path is None:
        raise FileNotFoundError(
            f"Could not find exact tag={tag} in CATALOG={CATALOG}."
        )
    return path


def get_path_from_catalog(tag: str) -> Path:
    """
    Args:
        tag (str):

    Returns:
        A file path.
    """
    path = _find_exact_catalog_path(tag)
    if path is None and not tag.startswith(f"{LOCAL_CANDIDATE_TAG_PREFIX}/"):
        path = _find_exact_catalog_path(get_local_candidate_tag(tag))

    if path is None:
        raise FileNotFoundError(
            f'Could not find tag={tag} in CATALOG={CATALOG}. '
            f'Please download using `lexnlp.ml.catalog.download.download_github_release("{tag}")`'
        )
    else:
        return path
