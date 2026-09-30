"""Reuse runtime catalog trust checks before model or corpus deserialization."""

from pathlib import Path


def ensure_tag_downloaded(tag: str) -> Path:
    """Verify pinned exact assets while preserving private candidate aliases.

    Explicit custom/local tags retain runtime behavior. An absent remote tag
    must belong to the reviewed manifest before it can be downloaded.
    """
    from lexnlp.extract.en.contracts.runtime_model import ensure_tag_downloaded as ensure_verified_tag
    from lexnlp.ml.catalog import (
        get_exact_path_from_catalog,
        get_local_candidate_tag,
        get_path_from_catalog,
    )

    try:
        get_exact_path_from_catalog(tag)
    except FileNotFoundError:
        try:
            get_path_from_catalog(tag)
        except FileNotFoundError:
            return ensure_verified_tag(tag)
        return ensure_verified_tag(get_local_candidate_tag(tag))
    return ensure_verified_tag(tag)
