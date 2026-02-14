#!/usr/bin/env python3
"""Verify that required release-tag assets exist and match pinned hashes.

This is intended for scheduled CI ("asset drift") to catch situations where
release assets disappear or are replaced under the same tag.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, Sequence


DEFAULT_MANIFEST = Path("test_data/model_quality/release_asset_manifest.json")


class DriftError(Exception):
    pass


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help=f"Manifest JSON path (default: {DEFAULT_MANIFEST})",
    )
    parser.add_argument(
        "--download-missing",
        action="store_true",
        help="Download missing tags before verifying hashes.",
    )
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Always re-download tags before verifying hashes (recommended for scheduled CI).",
    )
    return parser.parse_args(argv)


def load_manifest(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Manifest file not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Manifest JSON must be an object")
    assets = payload.get("assets")
    if not isinstance(assets, list) or not assets:
        raise ValueError("Manifest JSON must contain a non-empty 'assets' list")
    return payload


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_assets(payload: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    for item in payload["assets"]:
        if not isinstance(item, dict):
            raise ValueError("Manifest assets must be objects")
        for key in ("tag", "filename", "sha256"):
            if key not in item:
                raise ValueError(f"Manifest asset missing key={key}")
        yield item


def ensure_tag_downloaded(tag: str) -> Path:
    from lexnlp.ml.catalog import get_path_from_catalog
    from lexnlp.ml.catalog.download import download_github_release

    try:
        return get_path_from_catalog(tag)
    except FileNotFoundError:
        download_github_release(tag, prompt_user=False)
        return get_path_from_catalog(tag)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    payload = load_manifest(args.manifest)

    failures: list[str] = []

    for asset in iter_assets(payload):
        tag = str(asset["tag"]).strip()
        expected_name = str(asset["filename"]).strip()
        expected_sha = str(asset["sha256"]).strip().lower()
        expected_size = asset.get("size")

        try:
            from lexnlp.ml.catalog import get_path_from_catalog
            from lexnlp.ml.catalog.download import download_github_release

            if args.force_download:
                download_github_release(tag, prompt_user=False)
                path = get_path_from_catalog(tag)
            elif args.download_missing:
                path = ensure_tag_downloaded(tag)
            else:
                path = get_path_from_catalog(tag)
        except Exception as exc:
            failures.append(f"{tag}: missing/unreadable ({exc})")
            continue

        if path.name != expected_name:
            failures.append(f"{tag}: unexpected filename {path.name!r} (expected {expected_name!r})")
            continue

        if expected_size is not None:
            try:
                expected_size_int = int(expected_size)
            except (TypeError, ValueError):
                failures.append(f"{tag}: invalid manifest size={expected_size!r}")
                continue
            actual_size = path.stat().st_size
            if actual_size != expected_size_int:
                failures.append(f"{tag}: size mismatch {actual_size} != {expected_size_int}")
                continue

        actual_sha = sha256_file(path)
        if actual_sha.lower() != expected_sha:
            failures.append(f"{tag}: sha256 mismatch {actual_sha} != {expected_sha}")
            continue

        print(f"asset-drift: OK {tag} ({path.name})")

    if failures:
        for failure in failures:
            print(f"asset-drift: ERROR {failure}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
