"""Security and compatibility tests for catalog release downloads."""

from __future__ import annotations

import hashlib
import json
import stat
from base64 import b64encode
from pathlib import Path

import pytest

from lexnlp.ml.catalog import download


class FakeResponse:
    def __init__(self, payload: bytes, *, content_length: int | None = None):
        self.payload = payload
        self.headers = {}
        if content_length is not None:
            self.headers["Content-Length"] = str(content_length)

    def raise_for_status(self) -> None:
        return None

    def iter_content(self, chunk_size: int):
        for offset in range(0, len(self.payload), chunk_size):
            yield self.payload[offset : offset + chunk_size]


def trusted_asset(tag: str, filename: str, payload: bytes) -> download.TrustedAsset:
    return download.TrustedAsset(
        tag=tag,
        filename=filename,
        size=len(payload),
        sha256=hashlib.sha256(payload).hexdigest(),
    )


def test_get_asset_preserves_legacy_index_and_supports_trusted_filename():
    class ReleaseResponse:
        @staticmethod
        def json():
            return {
                "assets": [
                    {"name": "first.bin"},
                    {"name": "second.bin"},
                ]
            }

    response = ReleaseResponse()

    assert download.GitHubReleaseDownloader.get_asset(response, 1)["name"] == "second.bin"
    assert (
        download.GitHubReleaseDownloader.get_asset(
            response,
            filename="first.bin",
        )["name"]
        == "first.bin"
    )


def test_get_tag_preserves_legacy_deferred_status_handling(monkeypatch):
    response = object()
    monkeypatch.setattr(download, "get", lambda **_kwargs: response)

    assert download.GitHubReleaseDownloader.get_tag("pipeline/example/1") is response


def test_verify_md5_preserves_legacy_public_helper(tmp_path: Path):
    payload = b"legacy checksum payload"
    path = tmp_path / "payload.bin"
    path.write_bytes(payload)
    checksum = b64encode(
        hashlib.md5(payload, usedforsecurity=False).digest()
    ).decode()

    download.GitHubReleaseDownloader.verify_md5(path, checksum)

    with pytest.raises(download.ChecksumError, match="MD5"):
        download.GitHubReleaseDownloader.verify_md5(path, "not-the-checksum")


def test_legacy_download_asset_call_infers_unique_trusted_entry(
    monkeypatch,
    tmp_path: Path,
):
    payload = b"reviewed model payload"
    trusted = trusted_asset("pipeline/example/1", "model.bin", payload)
    manifest = download.AssetManifest(
        models_repo=(
            "https://api.github.com/repos/LexPredict/"
            "lexpredict-lexnlp/releases/tags/"
        ),
        assets={trusted.tag: trusted},
    )
    asset = {
        "name": trusted.filename,
        "size": trusted.size,
        "url": "https://api.github.com/repos/reviewed/models/releases/assets/1",
    }
    monkeypatch.setattr(download, "load_asset_manifest", lambda: manifest)
    monkeypatch.setattr(download, "get_models_repo", lambda: manifest.models_repo)
    monkeypatch.setattr(
        download,
        "get",
        lambda **_kwargs: FakeResponse(payload, content_length=len(payload)),
    )

    result = download.GitHubReleaseDownloader.download_asset(asset, tmp_path)
    path = tmp_path / trusted.filename

    assert result is None
    assert path.read_bytes() == payload


def test_legacy_release_downloaders_return_exact_none(monkeypatch, tmp_path: Path):
    sentinel = tmp_path / "verified.bin"
    sentinel.write_bytes(b"verified")
    forces = []

    def fake_download_to_path(
        cls,
        tag,
        *,
        manifest_path=None,
        force=False,
    ):
        assert tag == "pipeline/is-contract/0.1"
        assert manifest_path is None
        forces.append(force)
        return sentinel

    monkeypatch.setattr(
        download.GitHubReleaseDownloader,
        "download_release_to_path",
        classmethod(fake_download_to_path),
    )

    assert (
        download.GitHubReleaseDownloader.download_release(
            "pipeline/is-contract/0.1",
        )
        is None
    )
    assert (
        download.download_github_release(
            "pipeline/is-contract/0.1",
            prompt_user=False,
        )
        is None
    )
    assert (
        download.download_github_release_to_path(
            "pipeline/is-contract/0.1",
            force=True,
        )
        == sentinel
    )
    assert forces == [False, False, True]


def test_legacy_models_repo_assignment_and_environment_precedence(monkeypatch):
    import lexnlp

    calls = []

    class Response:
        pass

    monkeypatch.delenv("LEXNLP_MODELS_REPO", raising=False)
    monkeypatch.delenv("LEXNLP_MODELS_REPO_SLUG", raising=False)
    monkeypatch.setattr(
        lexnlp,
        "MODELS_REPO",
        "https://api.github.com/repos/legacy/root/releases/tags",
    )
    monkeypatch.setattr(download, "get", lambda **kwargs: calls.append(kwargs) or Response())

    download.GitHubReleaseDownloader.get_tag("pipeline/example/1")

    assert lexnlp.get_models_repo() == (
        "https://api.github.com/repos/legacy/root/releases/tags/"
    )
    assert calls[-1]["url"].startswith(
        "https://api.github.com/repos/legacy/root/releases/tags/"
    )

    monkeypatch.setattr(
        download,
        "MODELS_REPO",
        "https://api.github.com/repos/legacy/download-module/releases/tags/",
    )
    download.GitHubReleaseDownloader.get_tag("pipeline/example/2")
    assert calls[-1]["url"].startswith(
        "https://api.github.com/repos/legacy/download-module/releases/tags/"
    )

    monkeypatch.setenv("LEXNLP_MODELS_REPO_SLUG", "environment/wins")
    download.GitHubReleaseDownloader.get_tag("pipeline/example/3")
    assert calls[-1]["url"].startswith(
        "https://api.github.com/repos/environment/wins/releases/tags/"
    )


def test_packaged_manifest_covers_legacy_contract_model_and_corpora():
    manifest = download.load_asset_manifest()

    assert manifest.models_repo == (
        "https://api.github.com/repos/LexPredict/lexpredict-lexnlp/releases/tags/"
    )
    assert manifest.get("pipeline/is-contract/0.1").filename == (
        "pipeline_is_contract_classifier.cloudpickle"
    )
    assert manifest.get("pipeline/is-contract/0.2").sha256 == (
        "083bab9998e1b0d858b7a348f17c09af984264744b680407541723647cfbe9f6"
    )
    assert manifest.get("pipeline/contract-type/0.2-runtime").sha256 == (
        "3b04a8a96e841a200dd85ba080ee14140be6a4a554e511dfd75d6dc080a9fab7"
    )
    assert manifest.get("corpus/contract-types/0.1").size == 16_644_740


def test_runtime_and_quality_gate_release_manifests_are_byte_identical():
    repository_root = Path(__file__).resolve().parents[4]

    assert (
        repository_root
        / "lexnlp/ml/catalog/release_asset_manifest.json"
    ).read_bytes() == (
        repository_root
        / "test_data/model_quality/release_asset_manifest.json"
    ).read_bytes()


def test_unlisted_tag_is_rejected_before_any_network_request(monkeypatch):
    def fail_if_called(*_args, **_kwargs):
        pytest.fail("network must not be reached for an untrusted tag")

    monkeypatch.setattr(download, "get", fail_if_called)

    with pytest.raises(download.MissingTrustedAssetError, match="not present"):
        download.download_github_release(
            "pipeline/unreviewed/9.9",
            prompt_user=False,
        )


def test_custom_repository_requires_a_matching_reviewed_manifest(
    monkeypatch,
    tmp_path: Path,
):
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "models_repo_slug": "reviewed/models",
                "assets": [
                    {
                        "tag": "pipeline/example/1",
                        "filename": "model.bin",
                        "size": 1,
                        "sha256": hashlib.sha256(b"x").hexdigest(),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("LEXNLP_MODELS_REPO_SLUG", "different/models")

    with pytest.raises(download.AssetTrustError, match="not the repository"):
        download.download_github_release(
            "pipeline/example/1",
            prompt_user=False,
            manifest_path=manifest_path,
        )


@pytest.mark.parametrize(
    "tag,filename",
    [
        ("../outside", "model.bin"),
        ("/absolute", "model.bin"),
        (r"..\outside", "model.bin"),
        (r"pipeline\..\..\outside", "model.bin"),
        (r"C:\outside", "model.bin"),
        (r"\\server\share\outside", "model.bin"),
        ("pipeline/example/1", "../model.bin"),
        ("pipeline/example/1", r"..\model.bin"),
    ],
)
def test_manifest_rejects_unsafe_catalog_paths(
    tmp_path: Path,
    tag: str,
    filename: str,
):
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "models_repo_slug": "reviewed/models",
                "assets": [
                    {
                        "tag": tag,
                        "filename": filename,
                        "size": 1,
                        "sha256": hashlib.sha256(b"x").hexdigest(),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(download.AssetTrustError, match="paths|path-free"):
        download.load_asset_manifest(manifest_path)


def test_release_asset_host_must_match_manifest_repository(
    monkeypatch,
    tmp_path: Path,
):
    payload = b"reviewed"
    trusted = trusted_asset("pipeline/example/1", "model.bin", payload)
    asset = {
        "name": trusted.filename,
        "size": trusted.size,
        "url": "https://attacker.example.test/releases/assets/1",
    }

    def fail_if_called(*_args, **_kwargs):
        pytest.fail("an untrusted asset host must fail before network access")

    monkeypatch.setattr(download, "get", fail_if_called)

    with pytest.raises(download.AssetTrustError, match="absolute HTTPS URL"):
        download.GitHubReleaseDownloader.download_asset(
            asset,
            tmp_path,
            trusted=trusted,
            expected_host="api.github.com",
        )


def test_release_destination_cannot_escape_catalog_through_symlink(
    monkeypatch,
    tmp_path: Path,
):
    payload = b"reviewed"
    trusted = trusted_asset("pipeline/example/1", "model.bin", payload)
    manifest = download.AssetManifest(
        models_repo=(
            "https://api.github.com/repos/LexPredict/"
            "lexpredict-lexnlp/releases/tags/"
        ),
        assets={trusted.tag: trusted},
    )
    catalog = tmp_path / "catalog"
    external = tmp_path / "external"
    catalog.mkdir()
    external.mkdir()
    try:
        (catalog / "pipeline").symlink_to(external, target_is_directory=True)
    except OSError as error:
        pytest.skip(f"directory symlinks unavailable: {error}")

    monkeypatch.setattr(download, "CATALOG", catalog)
    monkeypatch.setattr(download, "load_asset_manifest", lambda _path=None: manifest)
    monkeypatch.setattr(
        download.GitHubReleaseDownloader,
        "get_tag",
        lambda *_args, **_kwargs: pytest.fail(
            "unsafe destinations must fail before network access"
        ),
    )

    with pytest.raises(download.AssetTrustError, match="escapes"):
        download.GitHubReleaseDownloader.download_release_to_path(trusted.tag)


def test_verified_asset_is_installed_atomically(monkeypatch, tmp_path: Path):
    payload = b"reviewed model payload"
    trusted = trusted_asset("pipeline/example/1", "model.bin", payload)
    asset = {
        "name": trusted.filename,
        "size": trusted.size,
        "url": "https://api.github.com/repos/reviewed/models/releases/assets/1",
    }
    monkeypatch.setattr(
        download,
        "get",
        lambda **_kwargs: FakeResponse(payload, content_length=len(payload)),
    )

    path = download.GitHubReleaseDownloader.download_asset_to_path(
        asset,
        tmp_path,
        trusted=trusted,
        chunk_size=4,
    )

    assert path.read_bytes() == payload
    assert list(tmp_path.glob("*.part")) == []
    assert list(tmp_path.glob(".*.tmp")) == []
    assert stat.S_IMODE(path.stat().st_mode) == 0o644


def test_force_download_fetches_even_when_verified_cache_exists(
    monkeypatch,
    tmp_path: Path,
):
    payload = b"reviewed model payload"
    trusted = trusted_asset("pipeline/example/1", "model.bin", payload)
    destination = tmp_path / trusted.filename
    destination.write_bytes(payload)
    asset = {
        "name": trusted.filename,
        "size": trusted.size,
        "url": "https://api.github.com/repos/reviewed/models/releases/assets/1",
    }
    calls = []

    def fake_get(**kwargs):
        calls.append(kwargs)
        return FakeResponse(payload, content_length=len(payload))

    monkeypatch.setattr(download, "get", fake_get)

    path = download.GitHubReleaseDownloader.download_asset_to_path(
        asset,
        tmp_path,
        trusted=trusted,
        force=True,
    )

    assert path == destination
    assert destination.read_bytes() == payload
    assert len(calls) == 1


def test_verified_asset_preserves_existing_permissions(monkeypatch, tmp_path: Path):
    payload = b"reviewed model payload"
    trusted = trusted_asset("pipeline/example/1", "model.bin", payload)
    destination = tmp_path / trusted.filename
    destination.write_bytes(b"unverified old payload")
    destination.chmod(0o640)
    asset = {
        "name": trusted.filename,
        "size": trusted.size,
        "url": "https://api.github.com/repos/reviewed/models/releases/assets/1",
    }
    monkeypatch.setattr(
        download,
        "get",
        lambda **_kwargs: FakeResponse(payload, content_length=len(payload)),
    )

    path = download.GitHubReleaseDownloader.download_asset_to_path(
        asset,
        tmp_path,
        trusted=trusted,
    )

    assert path.read_bytes() == payload
    assert stat.S_IMODE(path.stat().st_mode) == 0o640


def test_local_artifact_verification_is_bound_to_manifest_bytes(tmp_path: Path):
    payload = b"reviewed model payload"
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "models_repo_slug": "reviewed/models",
                "assets": [
                    {
                        "tag": "pipeline/example/1",
                        "filename": "model.bin",
                        "size": len(payload),
                        "sha256": hashlib.sha256(payload).hexdigest(),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    artifact_path = tmp_path / "model.bin"
    artifact_path.write_bytes(payload)

    trusted = download.verify_trusted_asset_file(
        artifact_path,
        "pipeline/example/1",
        manifest_path=manifest_path,
    )

    assert trusted.size == len(payload)

    artifact_path.write_bytes(b"tampered model payload")
    with pytest.raises(download.ChecksumError, match="size|SHA-256"):
        download.verify_trusted_asset_file(
            artifact_path,
            "pipeline/example/1",
            manifest_path=manifest_path,
        )


def test_local_artifact_verification_rejects_wrong_filename(tmp_path: Path):
    payload = b"reviewed model payload"
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "models_repo_slug": "reviewed/models",
                "assets": [
                    {
                        "tag": "pipeline/example/1",
                        "filename": "model.bin",
                        "size": len(payload),
                        "sha256": hashlib.sha256(payload).hexdigest(),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    artifact_path = tmp_path / "other.bin"
    artifact_path.write_bytes(payload)

    with pytest.raises(download.AssetTrustError, match="filename"):
        download.verify_trusted_asset_file(
            artifact_path,
            "pipeline/example/1",
            manifest_path=manifest_path,
        )


def test_digest_failure_preserves_existing_asset_and_removes_temporary_file(
    monkeypatch,
    tmp_path: Path,
):
    expected_payload = b"expected payload"
    malicious_payload = b"malicious payload"
    trusted = trusted_asset("pipeline/example/1", "model.bin", expected_payload)
    destination = tmp_path / trusted.filename
    destination.write_bytes(b"previous unverified payload")
    asset = {
        "name": trusted.filename,
        "size": trusted.size,
        "url": "https://api.github.com/repos/reviewed/models/releases/assets/1",
    }
    padded_payload = malicious_payload[: trusted.size].ljust(trusted.size, b"!")
    monkeypatch.setattr(
        download,
        "get",
        lambda **_kwargs: FakeResponse(padded_payload, content_length=trusted.size),
    )

    with pytest.raises(download.ChecksumError, match="SHA-256"):
        download.GitHubReleaseDownloader.download_asset(
            asset,
            tmp_path,
            trusted=trusted,
            chunk_size=3,
        )

    assert destination.read_bytes() == b"previous unverified payload"
    assert list(tmp_path.glob("*.part")) == []


def test_oversized_response_is_rejected_before_install(monkeypatch, tmp_path: Path):
    expected_payload = b"small"
    trusted = trusted_asset("pipeline/example/1", "model.bin", expected_payload)
    asset = {
        "name": trusted.filename,
        "size": trusted.size,
        "url": "https://api.github.com/repos/reviewed/models/releases/assets/1",
    }
    monkeypatch.setattr(
        download,
        "get",
        lambda **_kwargs: FakeResponse(
            expected_payload + b"unexpected",
            content_length=None,
        ),
    )

    with pytest.raises(download.AssetTrustError, match="exceeded trusted size"):
        download.GitHubReleaseDownloader.download_asset(
            asset,
            tmp_path,
            trusted=trusted,
            chunk_size=2,
        )

    assert not (tmp_path / trusted.filename).exists()
    assert list(tmp_path.glob("*.part")) == []


def test_existing_verified_asset_avoids_network(monkeypatch, tmp_path: Path):
    payload = b"verified"
    trusted = trusted_asset("pipeline/example/1", "model.bin", payload)
    destination = tmp_path / trusted.filename
    destination.write_bytes(payload)
    asset = {
        "name": trusted.filename,
        "size": trusted.size,
        "url": "https://api.github.com/repos/reviewed/models/releases/assets/1",
    }

    def fail_if_called(*_args, **_kwargs):
        pytest.fail("verified cached files must not be downloaded again")

    monkeypatch.setattr(download, "get", fail_if_called)

    assert (
        download.GitHubReleaseDownloader.download_asset(
            asset,
            tmp_path,
            trusted=trusted,
        )
        is None
    )
    assert destination.read_bytes() == payload
