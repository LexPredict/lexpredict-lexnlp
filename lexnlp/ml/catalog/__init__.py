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
from pathlib import Path
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

_TAG_DICT_CACHE: Optional[Dict[str, Path]] = None


def _build_tag_dict() -> Dict[str, Path]:
    """
    Builds a dictionary with the following structure:

    - keys (str): directory paths relative to CATALOG, each corresponding to GitHub release tags.
    - values (Path): file path under the directory ("tag").

    Returns:
        A dictionary.
    """
    return {
        str(path.parent.relative_to(CATALOG)): path
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


def get_path_from_catalog(tag: str) -> Path:
    """
    Args:
        tag (str):

    Returns:
        A file path.
    """
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

    if path is None:
        raise FileNotFoundError(
            f'Could not find tag={tag} in CATALOG={CATALOG}. '
            f'Please download using `lexnlp.ml.catalog.download.download_github_release("{tag}")`'
        )
    else:
        return path
