"""Tests for deterministic external-asset bootstrapping."""

from __future__ import annotations

import hashlib
import io
import stat
import zipfile
from dataclasses import replace
from pathlib import Path

import pytest

from scripts import bootstrap_assets
from lexnlp.ml.catalog import download as catalog_download


class FakeDownload:
    def __init__(
        self,
        payload: bytes,
        url: str = "https://downloads.example.test/asset",
    ):
        self.payload = payload
        self.url = url
        self.offset = 0

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, size: int) -> bytes:
        chunk = self.payload[self.offset : self.offset + size]
        self.offset += len(chunk)
        return chunk

    def geturl(self) -> str:
        return self.url


def test_download_file_sha512_verifies_before_atomic_install(
    monkeypatch,
    tmp_path: Path,
):
    payload = b"official release bytes"
    monkeypatch.setattr(
        bootstrap_assets,
        "urlopen",
        lambda *_args, **_kwargs: FakeDownload(payload),
    )
    destination = tmp_path / "asset.jar"

    bootstrap_assets.download_file(
        "https://downloads.example.test/asset.jar",
        destination,
        expected_sha512=hashlib.sha512(payload).hexdigest(),
        force=False,
        dry_run=False,
        timeout=5,
    )

    assert destination.read_bytes() == payload
    assert not destination.with_name("asset.jar.part").exists()


def test_download_file_rejects_bad_digest_without_installing(
    monkeypatch,
    tmp_path: Path,
):
    payload = b"tampered bytes"
    monkeypatch.setattr(
        bootstrap_assets,
        "urlopen",
        lambda *_args, **_kwargs: FakeDownload(payload),
    )
    destination = tmp_path / "asset.jar"

    with pytest.raises(RuntimeError, match="SHA-512 verification failed"):
        bootstrap_assets.download_file(
            "https://downloads.example.test/asset.jar",
            destination,
            expected_sha512=hashlib.sha512(b"expected bytes").hexdigest(),
            force=False,
            dry_run=False,
            timeout=5,
        )

    assert not destination.exists()
    assert not destination.with_name("asset.jar.part").exists()


def test_download_file_enforces_size_limit(monkeypatch, tmp_path: Path):
    payload = b"too large"
    monkeypatch.setattr(bootstrap_assets, "MAX_EXTERNAL_ASSET_BYTES", 4)
    monkeypatch.setattr(
        bootstrap_assets,
        "urlopen",
        lambda *_args, **_kwargs: FakeDownload(payload),
    )
    destination = tmp_path / "asset.jar"

    with pytest.raises(RuntimeError, match="safety limit"):
        bootstrap_assets.download_file(
            "https://downloads.example.test/asset.jar",
            destination,
            expected_sha512=hashlib.sha512(payload).hexdigest(),
            force=False,
            dry_run=False,
            timeout=5,
        )

    assert not destination.exists()
    assert not destination.with_name("asset.jar.part").exists()


def test_existing_asset_must_still_match_pinned_digest(
    monkeypatch,
    tmp_path: Path,
):
    destination = tmp_path / "asset.jar"
    destination.write_bytes(b"wrong")

    def fail_if_called(*_args, **_kwargs):
        pytest.fail("an existing unverified file must fail before network access")

    monkeypatch.setattr(bootstrap_assets, "urlopen", fail_if_called)

    with pytest.raises(RuntimeError, match="SHA-512 verification failed"):
        bootstrap_assets.download_file(
            "https://downloads.example.test/asset.jar",
            destination,
            expected_sha512=hashlib.sha512(b"expected").hexdigest(),
            force=False,
            dry_run=False,
            timeout=5,
        )


@pytest.mark.parametrize(
    "url",
    (
        "http://downloads.example.test/asset.jar",
        "file:///tmp/asset.jar",
        "https://user:password@downloads.example.test/asset.jar",
    ),
)
def test_download_file_rejects_untrusted_url_before_network(
    monkeypatch,
    tmp_path: Path,
    url: str,
):
    monkeypatch.setattr(
        bootstrap_assets,
        "urlopen",
        lambda *_args, **_kwargs: pytest.fail("untrusted URLs must not reach the network"),
    )

    with pytest.raises(RuntimeError, match="HTTPS"):
        bootstrap_assets.download_file(
            url,
            tmp_path / "asset.jar",
            expected_sha512=hashlib.sha512(b"asset").hexdigest(),
            force=False,
            dry_run=False,
            timeout=5,
        )


def test_download_file_rejects_redirect_to_unapproved_host(monkeypatch, tmp_path: Path):
    payload = b"asset"
    monkeypatch.setattr(
        bootstrap_assets,
        "urlopen",
        lambda *_args, **_kwargs: FakeDownload(
            payload,
            url="https://redirected.example.test/asset.jar",
        ),
    )

    with pytest.raises(RuntimeError, match="approved host"):
        bootstrap_assets.download_file(
            "https://downloads.example.test/asset.jar",
            tmp_path / "asset.jar",
            expected_sha512=hashlib.sha512(payload).hexdigest(),
            allowed_hosts=frozenset({"downloads.example.test"}),
            force=False,
            dry_run=False,
            timeout=5,
        )


def test_download_file_supports_pinned_sha256(monkeypatch, tmp_path: Path):
    payload = b"sha256-pinned asset"
    monkeypatch.setattr(
        bootstrap_assets,
        "urlopen",
        lambda *_args, **_kwargs: FakeDownload(payload),
    )
    destination = tmp_path / "asset.zip"

    bootstrap_assets.download_file(
        "https://downloads.example.test/asset.zip",
        destination,
        expected_sha256=hashlib.sha256(payload).hexdigest(),
        expected_size=len(payload),
        force=False,
        dry_run=False,
        timeout=5,
    )

    assert destination.read_bytes() == payload


@pytest.mark.parametrize("explicit_default", (False, True))
def test_contract_model_bootstrap_falls_back_only_for_missing_default_tag(
    monkeypatch,
    explicit_default: bool,
):
    calls = []
    reexports = []

    def fake_download(tag, *, prompt_user):
        assert prompt_user is False
        calls.append(tag)
        if tag == "pipeline/is-contract/0.2":
            raise catalog_download.MissingTrustedAssetError("not present")

    monkeypatch.delenv("LEXNLP_CONTRACT_MODEL_TAG", raising=False)
    monkeypatch.delenv("LEXNLP_IS_CONTRACT_MODEL_TAG", raising=False)
    if explicit_default:
        monkeypatch.setenv(
            "LEXNLP_IS_CONTRACT_MODEL_TAG",
            "pipeline/is-contract/0.2",
        )
    monkeypatch.setattr(catalog_download, "download_github_release", fake_download)
    monkeypatch.setattr(
        bootstrap_assets,
        "reexport_contract_model_from_legacy",
        lambda **kwargs: reexports.append(kwargs),
    )

    bootstrap_assets.bootstrap_contract_model(
        dry_run=False,
        tag="pipeline/is-contract/0.2",
    )

    assert calls == [
        "pipeline/is-contract/0.2",
        "pipeline/is-contract/0.1",
    ]
    assert reexports == [
        {
            "source_tag": "pipeline/is-contract/0.1",
            "target_tag": "_local-candidates/pipeline/is-contract/0.2",
        }
    ]


def test_contract_model_bootstrap_propagates_reexport_failure(monkeypatch):
    calls = []

    def fake_download(tag, *, prompt_user):
        assert prompt_user is False
        calls.append(tag)
        if tag == "pipeline/is-contract/0.2":
            raise catalog_download.MissingTrustedAssetError("not present")

    def fail_reexport(**_kwargs):
        raise ValueError("invalid serialized candidate")

    monkeypatch.delenv("LEXNLP_CONTRACT_MODEL_TAG", raising=False)
    monkeypatch.delenv("LEXNLP_IS_CONTRACT_MODEL_TAG", raising=False)
    monkeypatch.setattr(catalog_download, "download_github_release", fake_download)
    monkeypatch.setattr(
        bootstrap_assets,
        "reexport_contract_model_from_legacy",
        fail_reexport,
    )

    with pytest.raises(RuntimeError, match="Failed to generate required"):
        bootstrap_assets.bootstrap_contract_model(
            dry_run=False,
            tag="pipeline/is-contract/0.2",
        )

    assert calls == [
        "pipeline/is-contract/0.2",
        "pipeline/is-contract/0.1",
    ]


@pytest.mark.parametrize(
    "failure",
    (
        catalog_download.AssetTrustError("repository mismatch"),
        catalog_download.ChecksumError("checksum mismatch"),
    ),
)
def test_contract_model_bootstrap_does_not_mask_other_trust_failures(
    monkeypatch,
    failure,
):
    calls = []

    def fake_download(tag, *, prompt_user):
        assert prompt_user is False
        calls.append(tag)
        raise failure

    monkeypatch.delenv("LEXNLP_CONTRACT_MODEL_TAG", raising=False)
    monkeypatch.delenv("LEXNLP_IS_CONTRACT_MODEL_TAG", raising=False)
    monkeypatch.setattr(catalog_download, "download_github_release", fake_download)

    with pytest.raises(type(failure), match="mismatch"):
        bootstrap_assets.bootstrap_contract_model(
            dry_run=False,
            tag="pipeline/is-contract/0.2",
        )

    assert calls == ["pipeline/is-contract/0.2"]


def test_custom_contract_model_tag_never_uses_implicit_fallback(monkeypatch):
    calls = []

    def fake_download(tag, *, prompt_user):
        assert prompt_user is False
        calls.append(tag)
        raise catalog_download.MissingTrustedAssetError("not present")

    custom_tag = "pipeline/is-contract/custom"
    monkeypatch.setenv("LEXNLP_IS_CONTRACT_MODEL_TAG", custom_tag)
    monkeypatch.setattr(catalog_download, "download_github_release", fake_download)

    with pytest.raises(catalog_download.MissingTrustedAssetError, match="not present"):
        bootstrap_assets.bootstrap_contract_model(
            dry_run=False,
            tag=custom_tag,
        )

    assert calls == [custom_tag]


def test_stanford_downloads_are_official_and_fully_pinned():
    assert len(bootstrap_assets.STANFORD_DOWNLOADS) == 2
    for archive in bootstrap_assets.STANFORD_DOWNLOADS:
        assert archive.url.startswith("https://downloads.cs.stanford.edu/nlp/software/")
        assert archive.size > 0
        assert len(archive.sha512) == 128
        int(archive.sha512, 16)
        assert archive.root_directory in archive.filename
        assert archive.required_members
        for required in archive.required_members:
            assert required.path.startswith(archive.root_directory + "/")
            assert required.size > 0
            assert len(required.sha512) == 128
            int(required.sha512, 16)


def test_safe_zip_extraction_installs_verified_single_root(tmp_path: Path):
    archive_path = tmp_path / "asset.zip"
    payload = b"verified runtime data"
    required = bootstrap_assets.RequiredArchiveMember(
        path="stanford-test/runtime.jar",
        size=len(payload),
        sha512=hashlib.sha512(payload).hexdigest(),
    )
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr(required.path, payload)

    destination = tmp_path / "install"
    bootstrap_assets.extract_zip_safely(
        archive_path,
        destination,
        expected_root="stanford-test",
        required_members=(required,),
        dry_run=False,
    )

    assert (destination / required.path).read_bytes() == payload


def test_safe_zip_extraction_rejects_path_traversal(tmp_path: Path):
    archive_path = tmp_path / "traversal.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("../outside.txt", b"unsafe")

    with pytest.raises(RuntimeError, match="Unsafe ZIP member path"):
        bootstrap_assets.extract_zip_safely(
            archive_path,
            tmp_path / "install",
            expected_root="stanford-test",
            required_members=(),
            dry_run=False,
        )

    assert not (tmp_path / "outside.txt").exists()


def test_safe_zip_extraction_rejects_symlink(tmp_path: Path):
    archive_path = tmp_path / "symlink.zip"
    symlink = zipfile.ZipInfo("stanford-test/runtime.jar")
    symlink.create_system = 3
    symlink.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr(symlink, "target")

    with pytest.raises(RuntimeError, match="Unsupported ZIP member type"):
        bootstrap_assets.extract_zip_safely(
            archive_path,
            tmp_path / "install",
            expected_root="stanford-test",
            required_members=(),
            dry_run=False,
        )


def test_tika_downloads_are_current_and_sha512_pinned():
    filenames = [entry[0] for entry in bootstrap_assets.TIKA_DOWNLOADS]

    assert filenames == [
        "tika-app-3.3.2.jar",
        "tika-server-standard-3.3.2.jar",
    ]
    for _filename, url, size, digest in bootstrap_assets.TIKA_DOWNLOADS:
        assert url.startswith("https://downloads.apache.org/tika/3.3.2/")
        assert size > 0
        assert len(digest) == 128
        int(digest, 16)


def _test_nltk_resource() -> tuple[bootstrap_assets.NltkResource, bytes]:
    payload_buffer = io.BytesIO()
    with zipfile.ZipFile(payload_buffer, "w") as archive:
        archive.writestr("test_resource/data.txt", b"verified resource data")
    payload = payload_buffer.getvalue()
    resource = bootstrap_assets.NltkResource(
        package_id="test_resource",
        subdir="tokenizers",
        size=len(payload),
        unzipped_size=len(b"verified resource data"),
        sha256=hashlib.sha256(payload).hexdigest(),
        unzip=True,
    )
    return resource, payload


def test_nltk_resources_are_fully_pinned():
    assert [resource.package_id for resource in bootstrap_assets.NLTK_RESOURCES] == [
        "punkt",
        "punkt_tab",
        "wordnet",
        "omw-1.4",
        "omw-2.0",
        "averaged_perceptron_tagger",
        "averaged_perceptron_tagger_eng",
        "maxent_ne_chunker",
        "maxent_ne_chunker_tab",
        "words",
    ]
    assert bootstrap_assets.NLTK_DATA_REVISION == (
        "550b6625bcef1f2abff2ff770a5a0d272c9c6b2a"
    )
    for resource in bootstrap_assets.NLTK_RESOURCES:
        assert resource.url == (
            "https://raw.githubusercontent.com/nltk/nltk_data/"
            f"{bootstrap_assets.NLTK_DATA_REVISION}/packages/"
            f"{resource.subdir}/{resource.package_id}.zip"
        )
        assert resource.size > 0
        assert resource.unzipped_size > 0
        assert len(resource.sha256) == 64
        int(resource.sha256, 16)


def test_bootstrap_nltk_installs_and_reuses_verified_cache(
    monkeypatch,
    tmp_path: Path,
):
    resource, payload = _test_nltk_resource()
    monkeypatch.setattr(bootstrap_assets, "NLTK_RESOURCES", (resource,))
    requests = []

    def fake_urlopen(request, **_kwargs):
        requests.append(request.full_url)
        return FakeDownload(payload, url=request.full_url)

    monkeypatch.setattr(bootstrap_assets, "urlopen", fake_urlopen)

    bootstrap_assets.bootstrap_nltk(
        download_dir=tmp_path,
        force=False,
        dry_run=False,
        timeout=5,
    )

    archive_path = tmp_path / "tokenizers" / "test_resource.zip"
    extracted_path = tmp_path / "tokenizers" / "test_resource" / "data.txt"
    assert archive_path.read_bytes() == payload
    assert extracted_path.read_bytes() == b"verified resource data"
    assert requests == [resource.url]

    requests.clear()
    bootstrap_assets.bootstrap_nltk(
        download_dir=tmp_path,
        force=False,
        dry_run=False,
        timeout=5,
    )
    assert requests == []


@pytest.mark.parametrize("cache_state", ("missing", "tampered"))
def test_bootstrap_nltk_repairs_extracted_resource_from_verified_archive(
    monkeypatch,
    tmp_path: Path,
    cache_state: str,
):
    resource, payload = _test_nltk_resource()
    monkeypatch.setattr(bootstrap_assets, "NLTK_RESOURCES", (resource,))
    monkeypatch.setattr(
        bootstrap_assets,
        "urlopen",
        lambda request, **_kwargs: FakeDownload(payload, url=request.full_url),
    )
    bootstrap_assets.bootstrap_nltk(
        download_dir=tmp_path,
        force=False,
        dry_run=False,
        timeout=5,
    )

    extracted_path = tmp_path / "tokenizers" / "test_resource" / "data.txt"
    if cache_state == "missing":
        extracted_path.unlink()
    else:
        extracted_path.write_bytes(b"tampered resource data")

    monkeypatch.setattr(
        bootstrap_assets,
        "urlopen",
        lambda *_args, **_kwargs: pytest.fail("verified archive must be reused"),
    )
    bootstrap_assets.bootstrap_nltk(
        download_dir=tmp_path,
        force=False,
        dry_run=False,
        timeout=5,
    )

    assert extracted_path.read_bytes() == b"verified resource data"


def test_bootstrap_nltk_replaces_tampered_archive(
    monkeypatch,
    tmp_path: Path,
):
    resource, payload = _test_nltk_resource()
    monkeypatch.setattr(bootstrap_assets, "NLTK_RESOURCES", (resource,))
    archive_path = tmp_path / "tokenizers" / "test_resource.zip"
    archive_path.parent.mkdir(parents=True)
    tampered_payload = bytearray(payload)
    tampered_payload[-1] ^= 1
    archive_path.write_bytes(tampered_payload)
    requests = []

    def fake_urlopen(request, **_kwargs):
        requests.append(request.full_url)
        return FakeDownload(payload, url=request.full_url)

    monkeypatch.setattr(
        bootstrap_assets,
        "urlopen",
        fake_urlopen,
    )

    bootstrap_assets.bootstrap_nltk(
        download_dir=tmp_path,
        force=False,
        dry_run=False,
        timeout=5,
    )

    assert archive_path.read_bytes() == payload
    assert requests == [resource.url]


def test_bootstrap_nltk_rejects_invalid_replacement_without_overwriting_cache(
    monkeypatch,
    tmp_path: Path,
):
    resource, payload = _test_nltk_resource()
    monkeypatch.setattr(bootstrap_assets, "NLTK_RESOURCES", (resource,))
    archive_path = tmp_path / "tokenizers" / "test_resource.zip"
    archive_path.parent.mkdir(parents=True)
    cached_payload = bytearray(payload)
    cached_payload[-1] ^= 1
    archive_path.write_bytes(cached_payload)

    remote_payload = bytearray(payload)
    remote_payload[-2] ^= 1
    monkeypatch.setattr(
        bootstrap_assets,
        "urlopen",
        lambda request, **_kwargs: FakeDownload(
            remote_payload,
            url=request.full_url,
        ),
    )

    with pytest.raises(RuntimeError, match="SHA-256 verification failed"):
        bootstrap_assets.bootstrap_nltk(
            download_dir=tmp_path,
            force=False,
            dry_run=False,
            timeout=5,
        )

    assert archive_path.read_bytes() == cached_payload
    assert not archive_path.with_name("test_resource.zip.part").exists()


def test_bootstrap_nltk_rejects_drifted_manifest(monkeypatch, tmp_path: Path):
    resource, _payload = _test_nltk_resource()
    drifted = replace(
        resource,
        url=f"https://raw.githubusercontent.com/nltk/nltk_data/"
        f"{bootstrap_assets.NLTK_DATA_REVISION}/"
        "packages/tokenizers/different.zip",
    )
    monkeypatch.setattr(bootstrap_assets, "NLTK_RESOURCES", (drifted,))

    with pytest.raises(RuntimeError, match="does not match its pinned install path"):
        bootstrap_assets.bootstrap_nltk(
            download_dir=tmp_path,
            force=False,
            dry_run=False,
            timeout=5,
        )

    assert not any(tmp_path.iterdir())


def test_bootstrap_nltk_dry_run_has_no_filesystem_side_effects(
    monkeypatch,
    tmp_path: Path,
):
    resource, _payload = _test_nltk_resource()
    monkeypatch.setattr(bootstrap_assets, "NLTK_RESOURCES", (resource,))
    destination = tmp_path / "nltk_data"
    monkeypatch.setattr(
        bootstrap_assets,
        "urlopen",
        lambda *_args, **_kwargs: pytest.fail("dry run must not use the network"),
    )

    bootstrap_assets.bootstrap_nltk(
        download_dir=destination,
        force=False,
        dry_run=True,
        timeout=5,
    )

    assert not destination.exists()
