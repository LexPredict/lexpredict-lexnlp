#!/usr/bin/env python3
"""Deterministic cross-platform bootstrap utility for LexNLP assets."""

from __future__ import annotations

import argparse
import hashlib
import logging
import os
import shutil
import stat
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

LOGGER = logging.getLogger("lexnlp.bootstrap")

REPO_ROOT = Path(__file__).resolve().parents[1]
STANFORD_DATA_SUBDIRECTORY = "stanford_nlp"
DEFAULT_TIKA_DIR = REPO_ROOT / "bin"
STANFORD_DOWNLOAD_HOSTS = frozenset({"downloads.cs.stanford.edu"})
TIKA_DOWNLOAD_HOSTS = frozenset({"downloads.apache.org"})

# Verified against nltk_data/index.xml and the archive bytes at this immutable
# upstream revision. The Downloader index's size, unzipped_size, SHA-256,
# subdir, and unzip fields are copied into NLTK_RESOURCES below.
NLTK_DATA_REVISION = "550b6625bcef1f2abff2ff770a5a0d272c9c6b2a"
NLTK_DATA_BASE_URL = (
    f"https://raw.githubusercontent.com/nltk/nltk_data/{NLTK_DATA_REVISION}/packages"
)
NLTK_DATA_HOSTS = frozenset({"raw.githubusercontent.com"})


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


@dataclass(frozen=True)
class RequiredArchiveMember:
    """A runtime-critical file expected inside a trusted archive."""

    path: str
    size: int
    sha512: str


@dataclass(frozen=True)
class NltkResource:
    """Pinned NLTK data package metadata."""

    package_id: str
    subdir: str
    size: int
    unzipped_size: int
    sha256: str
    unzip: bool
    url: str = ""

    def __post_init__(self) -> None:
        if not self.url:
            object.__setattr__(
                self,
                "url",
                f"{NLTK_DATA_BASE_URL}/{self.subdir}/{self.package_id}.zip",
            )


NLTK_RESOURCES: Tuple[NltkResource, ...] = (
    NltkResource(
        package_id="punkt",
        subdir="tokenizers",
        size=13_905_355,
        unzipped_size=37_245_719,
        sha256="51c3078994aeaf650bfc8e028be4fb42b4a0d177d41c012b6a983979653660ec",
        unzip=True,
    ),
    NltkResource(
        package_id="punkt_tab",
        subdir="tokenizers",
        size=4_319_076,
        unzipped_size=10_885_330,
        sha256="e57f64187974277726a3417ca6f181ec5403676c717672eef6a748a7b20e0106",
        unzip=True,
    ),
    NltkResource(
        package_id="wordnet",
        subdir="corpora",
        size=10_775_600,
        unzipped_size=36_353_991,
        sha256="cbda5ea6eef7f36a97a43d4a75f85e07fccbb4f23657d27b4ccbc93e2646ab59",
        unzip=False,
    ),
    NltkResource(
        package_id="omw-1.4",
        subdir="corpora",
        size=26_634_772,
        unzipped_size=96_786_003,
        sha256="3b941e664852f3297b6040236626065796a2aaf7d7f9eec8779a3beaa1096c2d",
        unzip=False,
    ),
    NltkResource(
        package_id="omw-2.0",
        subdir="corpora",
        size=28_567_474,
        unzipped_size=105_793_496,
        sha256="049c0de0a2d097f6d4d1c97394ea8422bba1faaa30f92e054f18efdb534423ed",
        unzip=False,
    ),
    NltkResource(
        package_id="averaged_perceptron_tagger",
        subdir="taggers",
        size=2_526_731,
        unzipped_size=6_138_625,
        sha256="e1f13cf2532daadfd6f3bc481a49859f0b8ea6432ccdcd83e6a49a5f19008de9",
        unzip=True,
    ),
    NltkResource(
        package_id="averaged_perceptron_tagger_eng",
        subdir="taggers",
        size=1_539_115,
        unzipped_size=5_703_817,
        sha256="6025f530624335c67d6547d44757b357b4e79bae030a0383e9887a92c1718f0b",
        unzip=True,
    ),
    NltkResource(
        package_id="maxent_ne_chunker",
        subdir="chunkers",
        size=13_404_747,
        unzipped_size=23_604_982,
        sha256="b7cdb936c551c06ef2cdc6227238c5ccc9c8c5259a11f99f4a937419d52af61b",
        unzip=True,
    ),
    NltkResource(
        package_id="maxent_ne_chunker_tab",
        subdir="chunkers",
        size=5_449_208,
        unzipped_size=14_621_652,
        sha256="1370234c7770045d0c50f41e08bc627ec92450324a946de14b93cd7d5e362a86",
        unzip=True,
    ),
    NltkResource(
        package_id="words",
        subdir="corpora",
        size=757_777,
        unzipped_size=2_498_552,
        sha256="54ed02917d6771dcc3e8141218960d020947f7f2ccfd9ac9b320979349746015",
        unzip=True,
    ),
)


@dataclass(frozen=True)
class StanfordArchive:
    """Pinned metadata for a Stanford archive used by LexNLP."""

    filename: str
    url: str
    size: int
    sha512: str
    root_directory: str
    required_members: Tuple[RequiredArchiveMember, ...]


STANFORD_DOWNLOADS: Tuple[StanfordArchive, ...] = (
    StanfordArchive(
        filename="stanford-postagger-full-2017-06-09.zip",
        url=(
            "https://downloads.cs.stanford.edu/nlp/software/"
            "stanford-postagger-full-2017-06-09.zip"
        ),
        size=134_295_971,
        sha512=(
            "1818486da7c98a390cff06e1051d1bac09d1fe14ffab2b1cf3f86989fe69aa62"
            "0e22f1b13fa1ddc28f062499647865ebce39528750c5822d8266fdb995b54141"
        ),
        root_directory="stanford-postagger-full-2017-06-09",
        required_members=(
            RequiredArchiveMember(
                path="stanford-postagger-full-2017-06-09/stanford-postagger.jar",
                size=3_669_310,
                sha512=(
                    "2defbc8e5110bcc4ec6c261b9722c63391e3e98893c22c619bab5469bdad35f72"
                    "4e6f2d10d99af29bd66770e399685af9a036ba98143217516b748b38dffddda"
                ),
            ),
            RequiredArchiveMember(
                path=(
                    "stanford-postagger-full-2017-06-09/models/"
                    "english-bidirectional-distsim.tagger"
                ),
                size=15_796_277,
                sha512=(
                    "56579ad7b388580ee49da8e96307ad64cd5ddac2c57e49966a622decbe23d34df"
                    "b3e8125e7cc2720eaddef915d47db706527055697e786f12763265f03e9f9a9"
                ),
            ),
        ),
    ),
    StanfordArchive(
        filename="stanford-ner-2017-06-09.zip",
        url=(
            "https://downloads.cs.stanford.edu/nlp/software/"
            "stanford-ner-2017-06-09.zip"
        ),
        size=179_646_721,
        sha512=(
            "6c4e16f3cda9c60de85f580672357e13b3698cb0e39dfb3a92f10d303893f364"
            "ecf97d2c8c340d9f4207c5f01715a0f669168c9db198ddf6882ca51f103ba5da"
        ),
        root_directory="stanford-ner-2017-06-09",
        required_members=(
            RequiredArchiveMember(
                path="stanford-ner-2017-06-09/stanford-ner.jar",
                size=4_646_069,
                sha512=(
                    "f92f43f7e414f09456b55da41a9d8c35c1724321908cd2ccb5174dd8d20c0df9"
                    "8b713b5a92beb2f802054167ba3ffbe95c34bbff7cb0310dcba615af039d41af"
                ),
            ),
            RequiredArchiveMember(
                path=(
                    "stanford-ner-2017-06-09/classifiers/"
                    "english.all.3class.distsim.crf.ser.gz"
                ),
                size=34_663_961,
                sha512=(
                    "c92e8112e445e0a374770b6f799c9d39d23ef7e34e13dfb9c11a3d4e80d45504"
                    "e3dd6e4b6434ebbff7642291cdf4a0ef9f51af9d3dc0640e77893f2262fdf9c4"
                ),
            ),
        ),
    ),
)

TIKA_DOWNLOADS: Tuple[Tuple[str, str, int, str], ...] = (
    (
        "tika-app-3.3.2.jar",
        "https://downloads.apache.org/tika/3.3.2/tika-app-3.3.2.jar",
        66_978_444,
        (
            "88c2032cba0d45feea361e6eebd2918bd04707614cdda5d89a1b167da5503c98"
            "e7b4cd368336f0402d559abcaf5006fcc7c825c32c749ae0417ea2f3b8423aba"
        ),
    ),
    (
        "tika-server-standard-3.3.2.jar",
        "https://downloads.apache.org/tika/3.3.2/tika-server-standard-3.3.2.jar",
        76_497_574,
        (
            "fb1f2fe57ac458b09d44d41d816f582e1d2fc93488acff6275caf414d8d5ef94"
            "e42166edc0b488dc2fb6ef3aa21fab62b107c43b9060385ff6d675e393c2c9e9"
        ),
    ),
)

MAX_EXTERNAL_ASSET_BYTES = 512 * 1024 * 1024
MAX_ARCHIVE_UNCOMPRESSED_BYTES = 1024 * 1024 * 1024


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
        help="Download and verify Stanford POS tagger and NER assets.",
    )
    parser.add_argument(
        "--tika",
        action="store_true",
        help="Download and SHA-512 verify Apache Tika 3.3.2 app/server jars.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all bootstrap tasks.",
    )
    parser.add_argument(
        "--stanford-dir",
        default=None,
        help=(
            "Stanford assets directory (default: the NLTK download directory/stanford_nlp). "
            "For custom locations, include this directory or its containing data root in NLTK_DATA."
        ),
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


def _validate_https_url(
    url: str,
    *,
    allowed_hosts: frozenset[str] | None = None,
) -> None:
    parsed = urlsplit(url)
    hostname = (parsed.hostname or "").rstrip(".").lower()
    if (
        parsed.scheme.lower() != "https"
        or not hostname
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise RuntimeError(
            f"External asset URL must use HTTPS without embedded credentials: {url!r}"
        )
    if allowed_hosts is not None and hostname not in allowed_hosts:
        raise RuntimeError(
            f"External asset URL does not use an approved host: {url!r}"
        )


def download_file(
    url: str,
    destination: Path,
    *,
    expected_sha512: str | None = None,
    expected_sha256: str | None = None,
    expected_size: int | None = None,
    allowed_hosts: frozenset[str] | None = None,
    force: bool,
    dry_run: bool,
    timeout: int,
) -> None:
    _validate_https_url(url, allowed_hosts=allowed_hosts)
    if (expected_sha512 is None) == (expected_sha256 is None):
        raise ValueError("Specify exactly one expected SHA-512 or SHA-256 digest")

    if destination.exists() and not force:
        if expected_sha512 is not None:
            verify_file(
                destination,
                expected_sha512=expected_sha512,
                expected_size=expected_size,
            )
        else:
            verify_sha256(
                destination,
                expected_sha256=expected_sha256,
                expected_size=expected_size,
            )
        LOGGER.info("Skipping verified existing file: %s", destination)
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
        algorithm = "sha512" if expected_sha512 is not None else "sha256"
        expected_digest = expected_sha512 or expected_sha256
        digest = hashlib.new(algorithm)
        bytes_written = 0
        with urlopen(request, timeout=timeout) as response, tmp_destination.open("wb") as output_file:
            final_url = response.geturl() if hasattr(response, "geturl") else url
            _validate_https_url(final_url, allowed_hosts=allowed_hosts)
            while True:
                chunk = response.read(64 * 1024)
                if not chunk:
                    break
                bytes_written += len(chunk)
                if bytes_written > MAX_EXTERNAL_ASSET_BYTES:
                    raise RuntimeError(
                        f"Download exceeds {MAX_EXTERNAL_ASSET_BYTES} byte safety limit: {url}"
                    )
                digest.update(chunk)
                output_file.write(chunk)

        received_digest = digest.hexdigest()
        if expected_size is not None and bytes_written != expected_size:
            raise RuntimeError(
                "Size verification failed for {}: received={}, expected={}".format(
                    destination.name,
                    bytes_written,
                    expected_size,
                )
            )
        if received_digest != expected_digest:
            digest_name = algorithm.upper().replace("SHA", "SHA-")
            raise RuntimeError(
                "{} verification failed for {}: received={}, expected={}".format(
                    digest_name,
                    destination.name,
                    received_digest,
                    expected_digest,
                )
            )
        tmp_destination.replace(destination)
    except Exception:
        if tmp_destination.exists():
            tmp_destination.unlink()
        raise

    LOGGER.info("Saved %s", destination)


def verify_file(
    path: Path,
    *,
    expected_sha512: str,
    expected_size: int | None = None,
) -> None:
    if expected_size is not None:
        received_size = path.stat().st_size
        if received_size != expected_size:
            raise RuntimeError(
                "Size verification failed for {}: received={}, expected={}".format(
                    path,
                    received_size,
                    expected_size,
                )
            )

    digest = hashlib.sha512()
    with path.open("rb") as input_file:
        for chunk in iter(lambda: input_file.read(1024 * 1024), b""):
            digest.update(chunk)
    received_sha512 = digest.hexdigest()
    if received_sha512 != expected_sha512:
        raise RuntimeError(
            "SHA-512 verification failed for {}: received={}, expected={}".format(
                path,
                received_sha512,
                expected_sha512,
            )
        )


def verify_sha256(
    path: Path,
    *,
    expected_sha256: str,
    expected_size: int | None = None,
) -> None:
    if expected_size is not None:
        received_size = path.stat().st_size
        if received_size != expected_size:
            raise RuntimeError(
                "Size verification failed for {}: received={}, expected={}".format(
                    path,
                    received_size,
                    expected_size,
                )
            )

    digest = hashlib.sha256()
    with path.open("rb") as input_file:
        for chunk in iter(lambda: input_file.read(1024 * 1024), b""):
            digest.update(chunk)
    received_sha256 = digest.hexdigest()
    if received_sha256 != expected_sha256:
        raise RuntimeError(
            "SHA-256 verification failed for {}: received={}, expected={}".format(
                path,
                received_sha256,
                expected_sha256,
            )
        )


def verify_sha512(path: Path, expected_sha512: str) -> None:
    """Backward-compatible digest-only verifier."""

    verify_file(path, expected_sha512=expected_sha512)


def download_many(
    downloads: Iterable[Tuple[str, str, int, str]],
    destination_dir: Path,
    *,
    allowed_hosts: frozenset[str] | None = None,
    force: bool,
    dry_run: bool,
    timeout: int,
) -> None:
    for filename, url, expected_size, expected_sha512 in downloads:
        destination = destination_dir / filename
        download_file(
            url,
            destination,
            expected_sha512=expected_sha512,
            expected_size=expected_size,
            allowed_hosts=allowed_hosts,
            force=force,
            dry_run=dry_run,
            timeout=timeout,
        )


def _validated_zip_parts(member_name: str, expected_root: str) -> Tuple[str, ...]:
    normalized = member_name.rstrip("/")
    if (
        not normalized
        or member_name.startswith("/")
        or "\\" in member_name
        or "\x00" in member_name
    ):
        raise RuntimeError(f"Unsafe ZIP member path: {member_name!r}")

    parts = tuple(normalized.split("/"))
    if any(part in {"", ".", ".."} for part in parts) or parts[0] != expected_root:
        raise RuntimeError(f"Unsafe ZIP member path: {member_name!r}")
    return parts


def _validated_zip_members(
    archive: zipfile.ZipFile,
    *,
    expected_root: str,
    expected_uncompressed_size: int | None = None,
) -> list[tuple[zipfile.ZipInfo, Tuple[str, ...]]]:
    seen_paths = set()
    total_uncompressed = 0
    validated_members = []
    for member in archive.infolist():
        parts = _validated_zip_parts(member.filename, expected_root)
        if parts in seen_paths:
            raise RuntimeError(f"Duplicate ZIP member path: {member.filename!r}")
        seen_paths.add(parts)

        file_type = stat.S_IFMT(member.external_attr >> 16)
        if file_type not in {0, stat.S_IFREG, stat.S_IFDIR}:
            raise RuntimeError(f"Unsupported ZIP member type: {member.filename!r}")
        if member.flag_bits & 0x1:
            raise RuntimeError(f"Encrypted ZIP member is not supported: {member.filename!r}")

        total_uncompressed += member.file_size
        if total_uncompressed > MAX_ARCHIVE_UNCOMPRESSED_BYTES:
            raise RuntimeError(
                "Archive exceeds {} byte uncompressed safety limit".format(
                    MAX_ARCHIVE_UNCOMPRESSED_BYTES,
                )
            )
        validated_members.append((member, parts))

    if (
        expected_uncompressed_size is not None
        and total_uncompressed != expected_uncompressed_size
    ):
        raise RuntimeError(
            "Archive uncompressed-size verification failed: received={}, expected={}".format(
                total_uncompressed,
                expected_uncompressed_size,
            )
        )
    return validated_members


def extract_zip_safely(
    archive_path: Path,
    destination_dir: Path,
    *,
    expected_root: str,
    required_members: Tuple[RequiredArchiveMember, ...],
    expected_uncompressed_size: int | None = None,
    dry_run: bool,
) -> None:
    """Validate and atomically install a single-root ZIP archive."""

    if dry_run:
        LOGGER.info("DRY RUN: would safely extract %s -> %s", archive_path, destination_dir)
        return

    LOGGER.info("Validating archive %s", archive_path)
    with zipfile.ZipFile(archive_path) as archive:
        validated_members = _validated_zip_members(
            archive,
            expected_root=expected_root,
            expected_uncompressed_size=expected_uncompressed_size,
        )

        required_paths = {tuple(item.path.split("/")) for item in required_members}
        archive_paths = {parts for _member, parts in validated_members}
        missing_members = required_paths.difference(archive_paths)
        if missing_members:
            missing_display = ", ".join("/".join(parts) for parts in sorted(missing_members))
            raise RuntimeError(f"Archive is missing required Stanford files: {missing_display}")

        ensure_directory(destination_dir, dry_run=False)
        with tempfile.TemporaryDirectory(
            prefix=f".{expected_root}.extract-",
            dir=destination_dir,
        ) as staging_name:
            staging_dir = Path(staging_name)
            for member, parts in validated_members:
                target = staging_dir.joinpath(*parts)
                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue

                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as source, target.open("wb") as output:
                    shutil.copyfileobj(source, output, length=1024 * 1024)
                if target.stat().st_size != member.file_size:
                    raise RuntimeError(f"Extracted size mismatch for {member.filename!r}")

            for required in required_members:
                verify_file(
                    staging_dir / required.path,
                    expected_sha512=required.sha512,
                    expected_size=required.size,
                )

            staged_root = staging_dir / expected_root
            final_root = destination_dir / expected_root
            with tempfile.TemporaryDirectory(
                prefix=f".{expected_root}.backup-",
                dir=destination_dir,
            ) as backup_name:
                backup_root = Path(backup_name) / expected_root
                had_existing_root = final_root.exists() or final_root.is_symlink()
                if had_existing_root:
                    final_root.replace(backup_root)
                try:
                    staged_root.replace(final_root)
                except Exception:
                    if had_existing_root and not final_root.exists():
                        backup_root.replace(final_root)
                    raise

    LOGGER.info("Installed verified archive: %s", expected_root)


def _required_members_are_verified(
    destination_dir: Path,
    required_members: Tuple[RequiredArchiveMember, ...],
) -> bool:
    try:
        for required in required_members:
            verify_file(
                destination_dir / required.path,
                expected_sha512=required.sha512,
                expected_size=required.size,
            )
    except (OSError, RuntimeError):
        return False
    return True


def _nltk_download_directory() -> Path:
    try:
        from nltk.downloader import Downloader
    except ImportError as error:
        raise RuntimeError(
            "nltk is required to select its asset directory. Install dependencies first."
        ) from error
    directory = Downloader().download_dir
    if directory is None:
        raise RuntimeError("NLTK could not determine a writable download directory")
    return Path(directory).expanduser().resolve()


def bootstrap_stanford_assets(
    destination_dir: Path | None = None,
    *,
    force: bool,
    dry_run: bool,
    timeout: int,
) -> None:
    if destination_dir is None:
        # NLTK's Java sandbox already trusts its data roots. Keep Stanford
        # inside the same root as --nltk instead of expanding that trust list.
        destination_dir = _nltk_download_directory() / STANFORD_DATA_SUBDIRECTORY
    ensure_directory(destination_dir, dry_run=dry_run)
    for asset in STANFORD_DOWNLOADS:
        archive_path = destination_dir / asset.filename
        download_file(
            asset.url,
            archive_path,
            expected_sha512=asset.sha512,
            expected_size=asset.size,
            allowed_hosts=STANFORD_DOWNLOAD_HOSTS,
            force=force,
            dry_run=dry_run,
            timeout=timeout,
        )
        if (
            not force
            and not dry_run
            and _required_members_are_verified(destination_dir, asset.required_members)
        ):
            LOGGER.info("Skipping verified extracted Stanford asset: %s", asset.filename)
            continue
        extract_zip_safely(
            archive_path,
            destination_dir,
            expected_root=asset.root_directory,
            required_members=asset.required_members,
            dry_run=dry_run,
        )

    if dry_run:
        return

    missing_or_invalid = [
        asset.filename
        for asset in STANFORD_DOWNLOADS
        if not _required_members_are_verified(destination_dir, asset.required_members)
    ]
    if missing_or_invalid:
        raise RuntimeError(
            "Missing or invalid Stanford assets after installation: "
            + ", ".join(missing_or_invalid)
        )


def _validate_nltk_resource(resource: NltkResource) -> None:
    expected_url = (
        f"{NLTK_DATA_BASE_URL}/{resource.subdir}/{resource.package_id}.zip"
    )
    if resource.url != expected_url:
        raise RuntimeError(
            f"NLTK resource {resource.package_id!r} does not match its pinned install path"
        )
    if (
        not resource.package_id
        or "/" in resource.package_id
        or "\\" in resource.package_id
        or resource.package_id in {".", ".."}
    ):
        raise RuntimeError(f"Invalid pinned NLTK package id: {resource.package_id!r}")
    if resource.subdir not in {"chunkers", "corpora", "taggers", "tokenizers"}:
        raise RuntimeError(
            f"Invalid pinned NLTK package subdirectory: {resource.subdir!r}"
        )
    if resource.size <= 0 or resource.unzipped_size <= 0:
        raise RuntimeError(f"Invalid pinned NLTK package size: {resource.package_id!r}")
    if len(resource.sha256) != 64:
        raise RuntimeError(f"Invalid pinned NLTK SHA-256: {resource.package_id!r}")
    try:
        int(resource.sha256, 16)
    except ValueError as error:
        raise RuntimeError(
            f"Invalid pinned NLTK SHA-256: {resource.package_id!r}"
        ) from error
    _validate_https_url(resource.url, allowed_hosts=NLTK_DATA_HOSTS)


def _stream_sha256(input_file) -> str:
    digest = hashlib.sha256()
    for chunk in iter(lambda: input_file.read(1024 * 1024), b""):
        digest.update(chunk)
    return digest.hexdigest()


def _extracted_nltk_resource_is_verified(
    archive_path: Path,
    destination_dir: Path,
    resource: NltkResource,
) -> bool:
    extracted_root = destination_dir / resource.package_id
    if not extracted_root.is_dir() or extracted_root.is_symlink():
        return False

    try:
        with zipfile.ZipFile(archive_path) as archive:
            members = _validated_zip_members(
                archive,
                expected_root=resource.package_id,
                expected_uncompressed_size=resource.unzipped_size,
            )
            expected_files = {
                Path(*parts)
                for member, parts in members
                if not member.is_dir()
            }
            actual_files = set()
            for path in extracted_root.rglob("*"):
                if path.is_symlink():
                    return False
                if path.is_file():
                    actual_files.add(path.relative_to(destination_dir))
                elif not path.is_dir():
                    return False
            if actual_files != expected_files:
                return False

            for member, parts in members:
                if member.is_dir():
                    continue
                target = destination_dir.joinpath(*parts)
                with archive.open(member) as archived_file, target.open("rb") as installed_file:
                    if _stream_sha256(archived_file) != _stream_sha256(installed_file):
                        return False
    except (OSError, RuntimeError, zipfile.BadZipFile):
        return False
    return True


def bootstrap_nltk(
    *,
    force: bool,
    dry_run: bool,
    timeout: int,
    download_dir: Path | None = None,
) -> None:
    for resource in NLTK_RESOURCES:
        _validate_nltk_resource(resource)

    if download_dir is None:
        if dry_run:
            for resource in NLTK_RESOURCES:
                LOGGER.info(
                    "DRY RUN: would install pinned NLTK resource %s/%s",
                    resource.subdir,
                    resource.package_id,
                )
            return
        download_dir = _nltk_download_directory()
    else:
        download_dir = Path(download_dir)

    ensure_directory(download_dir, dry_run=dry_run)
    for resource in NLTK_RESOURCES:
        archive_path = (
            download_dir
            / resource.subdir
            / f"{resource.package_id}.zip"
        )
        LOGGER.info("Installing pinned NLTK resource: %s", resource.package_id)
        try:
            download_file(
                resource.url,
                archive_path,
                expected_sha256=resource.sha256,
                expected_size=resource.size,
                allowed_hosts=NLTK_DATA_HOSTS,
                force=force,
                dry_run=dry_run,
                timeout=timeout,
            )
        except RuntimeError:
            if force or not archive_path.exists():
                raise
            LOGGER.warning(
                "Replacing unverified cached NLTK archive: %s",
                archive_path,
            )
            download_file(
                resource.url,
                archive_path,
                expected_sha256=resource.sha256,
                expected_size=resource.size,
                allowed_hosts=NLTK_DATA_HOSTS,
                force=True,
                dry_run=dry_run,
                timeout=timeout,
            )
        if dry_run or not resource.unzip:
            continue

        resource_dir = download_dir / resource.subdir
        if (
            not force
            and _extracted_nltk_resource_is_verified(
                archive_path,
                resource_dir,
                resource,
            )
        ):
            LOGGER.info(
                "Skipping verified extracted NLTK resource: %s",
                resource.package_id,
            )
            continue
        extract_zip_safely(
            archive_path,
            resource_dir,
            expected_root=resource.package_id,
            required_members=(),
            expected_uncompressed_size=resource.unzipped_size,
            dry_run=False,
        )

    if dry_run:
        return
    invalid_resources = [
        resource.package_id
        for resource in NLTK_RESOURCES
        if resource.unzip
        and not _extracted_nltk_resource_is_verified(
            download_dir / resource.subdir / f"{resource.package_id}.zip",
            download_dir / resource.subdir,
            resource,
        )
    ]
    if invalid_resources:
        raise RuntimeError(
            "Missing or invalid NLTK resources after installation: "
            + ", ".join(invalid_resources)
        )


def reexport_contract_model_from_legacy(
    *,
    source_tag: str,
    target_tag: str,
) -> Path:
    """Build and validate an exact target tag from a trusted legacy model."""

    import pickle

    from lexnlp.extract.en.contracts.predictors import ProbabilityPredictorIsContract
    from lexnlp.ml.artifact_io import atomic_output_path
    from lexnlp.ml.catalog import (
        get_catalog_directory,
        get_path_from_catalog,
        invalidate_catalog_cache,
    )
    from lexnlp.ml.catalog.download import (
        load_asset_manifest,
        verify_trusted_asset_payload,
    )
    from lexnlp.utils.unpickler import load_sklearn_model

    source_path = get_path_from_catalog(source_tag)
    destination_dir = get_catalog_directory(target_tag)
    destination_path = destination_dir / source_path.name
    destination_dir.mkdir(parents=True, exist_ok=True)
    trusted_target = load_asset_manifest().assets.get(target_tag)

    with source_path.open("rb") as source_file:
        pipeline = load_sklearn_model(source_file)

    # Validate and apply runtime compatibility patches before serialization.
    ProbabilityPredictorIsContract(pipeline=pipeline)

    with atomic_output_path(destination_path) as temporary_path:
        with temporary_path.open("wb") as destination_file:
            pickle.dump(
                pipeline,
                destination_file,
                protocol=pickle.HIGHEST_PROTOCOL,
            )
        # Do not publish the temporary bytes unless the production loader and
        # predictor can consume the exact serialized artifact.
        with temporary_path.open("rb") as candidate_file:
            candidate_pipeline = load_sklearn_model(candidate_file)
        ProbabilityPredictorIsContract(pipeline=candidate_pipeline)
        if trusted_target is not None:
            # A manifest-pinned release tag may only receive the exact reviewed
            # payload.  Runtime-generated candidates use a private local tag.
            verify_trusted_asset_payload(temporary_path, target_tag)
    invalidate_catalog_cache()

    LOGGER.info(
        "Generated contract model tag=%s at %s",
        target_tag,
        destination_path,
    )
    return destination_path


def bootstrap_contract_model(*, dry_run: bool, tag: str) -> None:
    if dry_run:
        LOGGER.info("DRY RUN: would download LexNLP model tag %s", tag)
        return

    try:
        from lexnlp.ml.catalog.download import (
            AssetTrustError,
            MissingTrustedAssetError,
            download_github_release,
        )
    except ImportError as error:
        raise RuntimeError(
            "Unable to import LexNLP catalog downloader. Ensure dependencies and editable install are in place."
        ) from error

    LOGGER.info("Downloading LexNLP contract model: %s", tag)
    try:
        download_github_release(tag, prompt_user=False)
        return
    except MissingTrustedAssetError as error:
        # A reviewed default candidate may intentionally precede publication
        # in a custom/older manifest.  It is safe to generate only under the
        # private local-candidate namespace.
        failure = error
        unpublished_default = True
    except AssetTrustError:
        # Manifest, repository, host, and checksum failures are trust failures,
        # not signals to generate an unrelated local replacement.
        raise
    except Exception as error:
        # A 404 means the reviewed tag has not been published yet.  Other
        # network/server failures remain visible to the caller.
        failure = error
        unpublished_default = False

    status_code = getattr(getattr(failure, "response", None), "status_code", None)
    legacy_tag = "pipeline/is-contract/0.1"

    if (
        tag == "pipeline/is-contract/0.2"
        and (status_code == 404 or unpublished_default)
    ):
        from lexnlp.ml.catalog import get_local_candidate_tag

        local_candidate_tag = get_local_candidate_tag(tag)
        LOGGER.warning(
            "Contract model release tag=%s is not yet published; "
            "bootstrapping legacy tag=%s and generating private local tag=%s",
            tag,
            legacy_tag,
            local_candidate_tag,
        )

        # Ensure the baseline tag is available locally.
        download_github_release(legacy_tag, prompt_user=False)

        try:
            reexport_contract_model_from_legacy(
                source_tag=legacy_tag,
                target_tag=local_candidate_tag,
            )
        except Exception as generation_error:
            raise RuntimeError(
                "Failed to generate required contract model "
                f"tag={tag!r} from legacy tag={legacy_tag!r}"
            ) from generation_error
        return
    raise failure


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
        tasks.append(
            (
                "nltk",
                lambda: bootstrap_nltk(
                    force=args.force,
                    dry_run=args.dry_run,
                    timeout=args.timeout,
                ),
            )
        )
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
        stanford_dir = (
            Path(args.stanford_dir).expanduser().resolve()
            if args.stanford_dir is not None else None
        )
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
                    allowed_hosts=TIKA_DOWNLOAD_HOSTS,
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
