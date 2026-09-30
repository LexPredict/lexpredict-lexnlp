"""Download verified LexNLP release assets into the local model catalog."""

from __future__ import annotations

import hashlib
import json
import logging
import os
from base64 import b64encode
from dataclasses import dataclass
from importlib.resources import files
from math import floor, log, pow
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Dict, Iterator, Mapping, Optional, Union
from urllib.parse import urlparse

from requests import Response, get
from tqdm import tqdm

from lexnlp import DEFAULT_MODELS_REPO, get_models_repo
from lexnlp.ml.artifact_io import atomic_output_path
from lexnlp.ml.catalog import CATALOG, invalidate_catalog_cache


LOGGER: logging.Logger = logging.getLogger(__name__)

DEFAULT_GITHUB_TIMEOUT_SECONDS = 60.0
DEFAULT_MANIFEST_RESOURCE = "release_asset_manifest.json"
ASSET_MANIFEST_ENV_VAR = "LEXNLP_ASSET_MANIFEST"

# Historical integrations imported or assigned this name directly on
# ``lexnlp.ml.catalog.download``.  Environment configuration is preferred at
# call time, but the compatibility alias remains effective when no override is
# configured.
MODELS_REPO: str = DEFAULT_MODELS_REPO


class AssetTrustError(RuntimeError):
    """Raised when a release asset is not covered by the trusted manifest."""


class MissingTrustedAssetError(AssetTrustError):
    """Raised when a requested release tag has no reviewed manifest entry."""


class ChecksumError(AssetTrustError):
    """Raised when a downloaded asset does not match its trusted digest."""


@dataclass(frozen=True)
class TrustedAsset:
    """Immutable verification metadata for one release asset."""

    tag: str
    filename: str
    size: int
    sha256: str


@dataclass(frozen=True)
class AssetManifest:
    """Trusted repository identity and release-asset verification metadata."""

    models_repo: str
    assets: Mapping[str, TrustedAsset]

    def get(self, tag: str) -> TrustedAsset:
        try:
            return self.assets[tag]
        except KeyError as error:
            raise MissingTrustedAssetError(
                f"Release tag {tag!r} is not present in the trusted asset manifest. "
                f"Update {DEFAULT_MANIFEST_RESOURCE!r}, or set {ASSET_MANIFEST_ENV_VAR} "
                "to a reviewed manifest for an explicitly configured model repository."
            ) from error


def _get_github_timeout_seconds() -> float:
    raw = (os.getenv("LEXNLP_GITHUB_TIMEOUT") or "").strip()
    if not raw:
        return DEFAULT_GITHUB_TIMEOUT_SECONDS
    try:
        timeout = float(raw)
    except ValueError:
        return DEFAULT_GITHUB_TIMEOUT_SECONDS
    return timeout if timeout > 0 else DEFAULT_GITHUB_TIMEOUT_SECONDS


def _normalise_repo_url(url: str) -> str:
    parsed = urlparse(url)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise AssetTrustError(f"Model repository must use an absolute HTTPS URL: {url!r}")
    return url.rstrip("/") + "/"


def _configured_models_repo() -> str:
    """Resolve the repository while retaining legacy assignment semantics."""
    if (os.getenv("LEXNLP_MODELS_REPO") or "").strip() or (
        os.getenv("LEXNLP_MODELS_REPO_SLUG") or ""
    ).strip():
        return get_models_repo()

    legacy_value = str(MODELS_REPO or "").strip()
    if legacy_value and legacy_value != DEFAULT_MODELS_REPO:
        return legacy_value if legacy_value.endswith("/") else f"{legacy_value}/"
    return get_models_repo()


def _validate_catalog_tag(tag: str) -> PurePosixPath:
    """Validate a release tag as a portable relative catalog path."""
    tag_path = PurePosixPath(tag)
    windows_path = PureWindowsPath(tag)
    if (
        not tag
        or "\\" in tag
        or tag_path.is_absolute()
        or windows_path.is_absolute()
        or bool(windows_path.drive)
        or bool(windows_path.root)
        or tag_path.as_posix() != tag
        or any(part in ("", ".", "..") for part in tag.split("/"))
    ):
        raise AssetTrustError("Manifest tags must be safe relative catalog paths")
    return tag_path


def _catalog_destination_directory(tag: str) -> Path:
    """Resolve a tag beneath CATALOG, rejecting traversal through symlinks."""
    tag_path = _validate_catalog_tag(tag)
    catalog_root = Path(CATALOG).resolve()
    destination = (catalog_root / Path(*tag_path.parts)).resolve()
    try:
        destination.relative_to(catalog_root)
    except ValueError as error:
        raise AssetTrustError(
            f"Release tag escapes the local catalog directory: {tag!r}"
        ) from error
    if destination == catalog_root:
        raise AssetTrustError("Release tag must name a directory beneath the catalog")
    return destination


def _manifest_source(path: Optional[Union[Path, str]] = None):
    configured_path = path or (os.getenv(ASSET_MANIFEST_ENV_VAR) or "").strip()
    if configured_path:
        return Path(configured_path).expanduser()
    return files("lexnlp.ml.catalog").joinpath(DEFAULT_MANIFEST_RESOURCE)


def load_asset_manifest(path: Optional[Union[Path, str]] = None) -> AssetManifest:
    """Load and validate the packaged or explicitly configured trust manifest."""

    source = _manifest_source(path)
    try:
        with source.open("r", encoding="utf-8") as manifest_file:
            payload = json.load(manifest_file)
    except (OSError, TypeError, json.JSONDecodeError) as error:
        raise AssetTrustError(f"Unable to load trusted asset manifest from {source!s}") from error

    if payload.get("schema_version", 1) != 1:
        raise AssetTrustError("Unsupported release asset manifest schema")

    repo_url = payload.get("models_repo_base_url")
    if not repo_url:
        repo_slug = str(payload.get("models_repo_slug", "")).strip().strip("/")
        if not repo_slug or repo_slug.count("/") != 1:
            raise AssetTrustError("Asset manifest must define models_repo_slug=owner/repository")
        repo_url = f"https://api.github.com/repos/{repo_slug}/releases/tags/"
    repo_url = _normalise_repo_url(str(repo_url))

    trusted_assets: Dict[str, TrustedAsset] = {}
    for entry in payload.get("assets", ()):
        try:
            tag = str(entry["tag"]).strip()
            raw_filename = str(entry["filename"])
            filename = Path(raw_filename).name
            size = int(entry["size"])
            sha256 = str(entry["sha256"]).lower()
        except (KeyError, TypeError, ValueError) as error:
            raise AssetTrustError("Malformed entry in trusted asset manifest") from error

        _validate_catalog_tag(tag)
        if not filename or filename != raw_filename or "/" in raw_filename or "\\" in raw_filename:
            raise AssetTrustError("Manifest tag and filename must be non-empty and path-free")
        if size <= 0:
            raise AssetTrustError(f"Manifest size must be positive for tag={tag!r}")
        if len(sha256) != 64 or any(character not in "0123456789abcdef" for character in sha256):
            raise AssetTrustError(f"Manifest SHA-256 is invalid for tag={tag!r}")
        if tag in trusted_assets:
            raise AssetTrustError(f"Duplicate release tag in asset manifest: {tag!r}")

        trusted_assets[tag] = TrustedAsset(
            tag=tag,
            filename=filename,
            size=size,
            sha256=sha256,
        )

    if not trusted_assets:
        raise AssetTrustError("Trusted asset manifest does not contain any assets")
    return AssetManifest(models_repo=repo_url, assets=trusted_assets)


def _build_github_headers(headers: Mapping[str, str]) -> Dict[str, str]:
    """Augment request headers with an optional GitHub token."""

    token: str = (os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN") or "").strip()
    merged_headers: Dict[str, str] = dict(headers)
    if token:
        merged_headers["Authorization"] = f"Bearer {token}"
    return merged_headers


def _require_matching_repository(manifest: AssetManifest) -> str:
    configured_repo = _normalise_repo_url(_configured_models_repo())
    if configured_repo != manifest.models_repo:
        raise AssetTrustError(
            "Configured model repository is not the repository named by the trusted "
            f"asset manifest: configured={configured_repo!r}, manifest={manifest.models_repo!r}"
        )
    return configured_repo


def _verify_file(path: Path, trusted: TrustedAsset) -> None:
    if not path.is_file():
        raise ChecksumError(f"Downloaded asset does not exist: {path}")
    if path.stat().st_size != trusted.size:
        raise ChecksumError(
            f"Asset size verification failed for {trusted.tag!r}: "
            f"received={path.stat().st_size}, expected={trusted.size}"
        )

    digest = hashlib.sha256()
    with path.open("rb") as asset_file:
        for chunk in iter(lambda: asset_file.read(1024 * 1024), b""):
            digest.update(chunk)
    received = digest.hexdigest()
    if received != trusted.sha256:
        raise ChecksumError(
            f"SHA-256 verification failed for {trusted.tag!r}: "
            f"received={received}, expected={trusted.sha256}"
        )


def verify_trusted_asset_file(
    path: Union[Path, str],
    tag: str,
    *,
    manifest_path: Optional[Union[Path, str]] = None,
) -> TrustedAsset:
    """Verify a local artifact against its reviewed manifest entry."""

    artifact_path = Path(path)
    trusted = load_asset_manifest(manifest_path).get(tag)
    if artifact_path.name != trusted.filename:
        raise AssetTrustError(
            f"Artifact filename does not match the trusted manifest for "
            f"tag={tag!r}: received={artifact_path.name!r}, "
            f"expected={trusted.filename!r}"
        )
    return verify_trusted_asset_payload(
        artifact_path,
        tag,
        manifest_path=manifest_path,
    )


def verify_trusted_asset_payload(
    path: Union[Path, str],
    tag: str,
    *,
    manifest_path: Optional[Union[Path, str]] = None,
) -> TrustedAsset:
    """Verify artifact bytes for a tag without constraining a staging filename."""
    artifact_path = Path(path)
    trusted = load_asset_manifest(manifest_path).get(tag)
    _verify_file(artifact_path, trusted)
    return trusted


class GitHubReleaseDownloader:
    """Download release assets only when covered by a trusted manifest."""

    @classmethod
    def download_release(
        cls,
        tag: str,
        *,
        manifest_path: Optional[Union[Path, str]] = None,
    ) -> None:
        """Legacy release downloader; successful calls return exactly ``None``."""
        cls.download_release_to_path(tag, manifest_path=manifest_path)
        return None

    @classmethod
    def download_release_to_path(
        cls,
        tag: str,
        *,
        manifest_path: Optional[Union[Path, str]] = None,
        force: bool = False,
    ) -> Path:
        """Download a verified release and return its installed file path."""
        manifest = load_asset_manifest(manifest_path)
        models_repo = _require_matching_repository(manifest)
        trusted = manifest.get(tag)
        destination_directory = _catalog_destination_directory(tag)
        response = cls.get_tag(tag, models_repo=models_repo)
        response.raise_for_status()
        asset = cls.get_asset(response, filename=trusted.filename)
        return cls.download_asset_to_path(
            asset,
            destination_directory,
            trusted=trusted,
            expected_host=urlparse(models_repo).hostname,
            force=force,
        )

    @staticmethod
    def get_tag(tag: str, *, models_repo: Optional[str] = None) -> Response:
        response: Response = get(
            url=f"{models_repo or _normalise_repo_url(_configured_models_repo())}{tag}",
            headers=_build_github_headers({"Accept": "application/vnd.github.v3+json"}),
            timeout=_get_github_timeout_seconds(),
        )
        return response

    @staticmethod
    def get_asset(
        response: Response,
        index: int = 0,
        *,
        filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return a release asset by legacy index or by trusted filename."""
        try:
            payload = response.json()
            assets = payload["assets"]
        except KeyError as error:
            if filename is None:
                raise KeyError(f"Available keys: {payload.keys()}") from error
            raise AssetTrustError(
                "GitHub release response does not contain an asset list"
            ) from error
        except (TypeError, ValueError) as error:
            raise AssetTrustError("GitHub release response does not contain an asset list") from error

        if filename is None:
            return assets[index]

        matches = [asset for asset in assets if asset.get("name") == filename]
        if len(matches) != 1:
            raise AssetTrustError(
                f"Expected exactly one release asset named {filename!r}; found {len(matches)}"
            )
        return matches[0]

    @staticmethod
    def verify_md5(
        filepath: Union[Path, str],
        checksum: str,
    ) -> None:
        """Verify a legacy Content-MD5 value.

        MD5 remains available for source compatibility with callers that used
        this public helper. Release installation never relies on it for trust;
        downloads require a manifest-bound SHA-256 digest.
        """
        digest = hashlib.md5(usedforsecurity=False)
        with Path(filepath).open("rb") as asset_file:
            for chunk in iter(lambda: asset_file.read(1024 * 1024), b""):
                digest.update(chunk)
        received = b64encode(digest.digest()).decode()
        if received != checksum:
            raise ChecksumError(
                "MD5 checksum verification failed! "
                f"Received: {received} Expected: {checksum}"
            )

    @staticmethod
    def yield_asset(
        content_iterator: Iterator[bytes],
        content_length: int,
        chunk_size: int,
    ) -> Iterator[bytes]:
        if content_length <= 0:
            raise ValueError("content_length must be positive")

        with tqdm(total=content_length, unit="iB", unit_scale=True) as progress_bar:
            for chunk in content_iterator:
                if not chunk:
                    continue
                progress_bar.update(len(chunk))
                yield chunk

    @classmethod
    def download_asset(
        cls,
        asset: Mapping[str, Any],
        destination_directory: Union[Path, str],
        *,
        trusted: Optional[TrustedAsset] = None,
        expected_host: Optional[str] = None,
        chunk_size: int = 8192,
    ) -> None:
        """Legacy asset downloader; successful calls return exactly ``None``."""
        cls.download_asset_to_path(
            asset,
            destination_directory,
            trusted=trusted,
            expected_host=expected_host,
            chunk_size=chunk_size,
        )
        return None

    @classmethod
    def download_asset_to_path(
        cls,
        asset: Mapping[str, Any],
        destination_directory: Union[Path, str],
        *,
        trusted: Optional[TrustedAsset] = None,
        expected_host: Optional[str] = None,
        chunk_size: int = 8192,
        force: bool = False,
    ) -> Path:
        """Download, bound, verify, and atomically install one trusted asset."""

        name = asset.get("name")
        advertised_size = int(asset.get("size", 0))
        if trusted is None:
            manifest = load_asset_manifest()
            models_repo = _require_matching_repository(manifest)
            matching_assets = [
                candidate
                for candidate in manifest.assets.values()
                if candidate.filename == name and candidate.size == advertised_size
            ]
            if len(matching_assets) != 1:
                raise AssetTrustError(
                    "Legacy download_asset calls must identify exactly one asset "
                    "in the trusted manifest by filename and size"
                )
            trusted = matching_assets[0]
            expected_host = expected_host or urlparse(models_repo).hostname

        if name != trusted.filename or advertised_size != trusted.size:
            raise AssetTrustError(
                f"Release metadata does not match the trusted manifest for tag={trusted.tag!r}"
            )

        asset_url = str(asset.get("url", ""))
        parsed_url = urlparse(asset_url)
        trusted_host = expected_host or urlparse(
            _normalise_repo_url(_configured_models_repo())
        ).hostname
        if (
            parsed_url.scheme != "https"
            or not parsed_url.hostname
            or parsed_url.hostname != trusted_host
            or parsed_url.username
            or parsed_url.password
        ):
            raise AssetTrustError(f"Release asset must use an absolute HTTPS URL: {asset_url!r}")

        destination_directory = Path(destination_directory)
        destination_directory.mkdir(exist_ok=True, parents=True)
        destination = destination_directory / trusted.filename
        if destination.exists() and not force:
            try:
                _verify_file(destination, trusted)
                LOGGER.info("Using verified existing asset %s", destination)
                return destination
            except ChecksumError:
                LOGGER.warning("Replacing unverified existing asset %s", destination)

        response: Response = get(
            url=asset_url,
            stream=True,
            headers=_build_github_headers({"Accept": "application/octet-stream"}),
            timeout=_get_github_timeout_seconds(),
        )
        response.raise_for_status()

        content_length_header = response.headers.get("Content-Length")
        if content_length_header is not None and int(content_length_header) != trusted.size:
            raise AssetTrustError(
                f"HTTP Content-Length does not match trusted size for tag={trusted.tag!r}"
            )

        bytes_written = 0
        with atomic_output_path(destination) as temporary_path:
            with temporary_path.open("wb") as temporary_file:
                for chunk in cls.yield_asset(
                    response.iter_content(chunk_size=chunk_size),
                    trusted.size,
                    chunk_size,
                ):
                    bytes_written += len(chunk)
                    if bytes_written > trusted.size:
                        raise AssetTrustError(
                            f"Asset exceeded trusted size for tag={trusted.tag!r}"
                        )
                    temporary_file.write(chunk)

            if bytes_written != trusted.size:
                raise ChecksumError(
                    f"Asset download was truncated for tag={trusted.tag!r}: "
                    f"received={bytes_written}, expected={trusted.size}"
                )
            _verify_file(temporary_path, trusted)

        invalidate_catalog_cache()
        LOGGER.info("Downloaded and verified %s to %s", trusted.tag, destination)
        return destination


def download_github_release(
    tag: str,
    prompt_user: bool = True,
    *,
    manifest_path: Optional[Union[Path, str]] = None,
) -> None:
    """Legacy release downloader; successful calls return exactly ``None``."""

    manifest = load_asset_manifest(manifest_path)
    _require_matching_repository(manifest)
    trusted = manifest.get(tag)

    if prompt_user:
        answer = input(
            f"Download verified `{tag}` ({_bytes_to_human_readable(trusted.size)}) "
            f"from {manifest.models_repo}? [Y/n] "
        ).strip().lower()
        if answer == "n":
            LOGGER.info("Not downloading %s", tag)
            return None
        if answer not in ("", "y"):
            raise ValueError("User input must be 'Y' or 'n'.")

    GitHubReleaseDownloader.download_release_to_path(
        tag,
        manifest_path=manifest_path,
    )
    return None


def download_github_release_to_path(
    tag: str,
    *,
    manifest_path: Optional[Union[Path, str]] = None,
    force: bool = False,
) -> Path:
    """Download a verified release without prompting and return its local path."""
    return GitHubReleaseDownloader.download_release_to_path(
        tag,
        manifest_path=manifest_path,
        force=force,
    )


def _bytes_to_human_readable(number_of_bytes: int) -> str:
    magnitude = int(floor(log(number_of_bytes, 1024)))
    value = number_of_bytes / pow(1024, magnitude)
    if magnitude > 3:
        return f"{value:.1f} TiB"
    return "{:3.2f} {}B".format(value, ("", "Ki", "Mi", "Gi")[magnitude])
