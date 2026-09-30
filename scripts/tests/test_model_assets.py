"""All model tooling checks pinned cached inputs before deserialization."""

import hashlib
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


SCRIPT_MODULES = [
    "reexport_contract_model", "model_quality_gate", "contract_type_quality_gate",
]


@pytest.fixture
def cached_asset(monkeypatch, tmp_path):
    from lexnlp.ml import catalog

    payload = b"reviewed pickle or corpus bytes"
    tag = "pipeline/is-contract/0.1"
    catalog_root = tmp_path / "catalog"
    path = catalog_root / tag / "model.bin"
    path.parent.mkdir(parents=True)
    path.write_bytes(payload)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({
        "schema_version": 1, "models_repo_slug": "reviewed/models",
        "assets": [{"tag": tag, "filename": path.name, "size": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest()}],
    }), encoding="utf-8")
    monkeypatch.setattr(catalog, "CATALOG", catalog_root)
    monkeypatch.setenv("LEXNLP_ASSET_MANIFEST", str(manifest))
    monkeypatch.setenv("LEXNLP_MODELS_REPO_SLUG", "reviewed/models")
    catalog.invalidate_catalog_cache()
    yield tag, path, catalog_root, manifest
    catalog.invalidate_catalog_cache()


@pytest.mark.parametrize("module_name", SCRIPT_MODULES)
def test_tool_rejects_tampered_pinned_cache_before_loading(monkeypatch, cached_asset, module_name):
    from lexnlp.ml.catalog import download
    from lexnlp.utils import unpickler

    tag, path, _, _ = cached_asset
    module = importlib.import_module("scripts." + module_name)
    assert module.ensure_tag_downloaded(tag) == path
    path.write_bytes(b"replaced untrusted executable pickle bytes")
    monkeypatch.setattr(unpickler, "load_sklearn_model",
                        lambda *args, **kwargs: pytest.fail("untrusted cached bytes must not reach unpickling"))
    monkeypatch.setattr(download, "download_github_release_to_path",
                        lambda *args, **kwargs: pytest.fail("checksum failure must not become a download fallback"))
    with pytest.raises(download.ChecksumError):
        if module_name == "reexport_contract_model":
            module.ensure_tag_downloaded(tag)
        else:
            module.load_pipeline_for_tag(tag)


def test_reexport_main_rejects_modified_source_before_unpickle_or_publication(monkeypatch, cached_asset):
    from lexnlp.ml import artifact_abi
    from lexnlp.ml.catalog import download
    from lexnlp.utils import unpickler
    from scripts import reexport_contract_model

    tag, path, root, _ = cached_asset
    path.write_bytes(b"replaced untrusted executable pickle")
    monkeypatch.setattr(artifact_abi, "assert_model_artifact_runtime", dict)
    monkeypatch.setattr(unpickler, "load_sklearn_model",
                        lambda *args, **kwargs: pytest.fail("changed source must fail before unpickling"))
    target = "local/reexport-candidate/1"
    with pytest.raises(download.ChecksumError):
        reexport_contract_model.main(["--source-tag", tag, "--target-tag", target])
    assert not (root / target).exists()


@pytest.mark.parametrize("module_name", SCRIPT_MODULES)
def test_tool_preserves_local_custom_tags_and_private_candidate_aliases(cached_asset, module_name):
    from lexnlp.ml import catalog

    _, _, root, _ = cached_asset
    module = importlib.import_module("scripts." + module_name)
    custom = root / "local/custom-model/v1/model.bin"
    custom.parent.mkdir(parents=True)
    custom.write_bytes(b"explicitly caller-trusted local model")
    candidate_tag = catalog.get_local_candidate_tag("pipeline/is-contract/0.2")
    candidate = root / candidate_tag / "model.bin"
    candidate.parent.mkdir(parents=True)
    candidate.write_bytes(b"local runtime candidate")
    catalog.invalidate_catalog_cache()
    assert module.ensure_tag_downloaded("local/custom-model/v1") == custom
    assert module.ensure_tag_downloaded(candidate_tag) == candidate
    assert module.ensure_tag_downloaded("pipeline/is-contract/0.2") == candidate


@pytest.mark.parametrize("module_name", SCRIPT_MODULES)
def test_unknown_remote_tag_is_rejected_before_network(monkeypatch, cached_asset, module_name):
    from lexnlp.ml.catalog import download

    module = importlib.import_module("scripts." + module_name)
    monkeypatch.setattr(download, "get", lambda *args, **kwargs: pytest.fail("unknown remote tag must not be requested"))
    with pytest.raises(download.MissingTrustedAssetError):
        module.ensure_tag_downloaded("pipeline/unknown-model/1")


@pytest.mark.parametrize("module_name", SCRIPT_MODULES)
@pytest.mark.parametrize("outside_checkout", [False, True], ids=["repository", "outside"])
def test_shared_helper_import_works_for_standalone_script_context(tmp_path, module_name, outside_checkout):
    project_root = Path(__file__).resolve().parents[2]
    script = project_root / "scripts" / f"{module_name}.py"
    code = """
import runpy
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1]).parent))
namespace = runpy.run_path(sys.argv[1], run_name='standalone_probe')
try:
    namespace['ensure_tag_downloaded']('pipeline/unknown-model/1')
except Exception as error:
    from lexnlp.ml.catalog.download import MissingTrustedAssetError
    if not isinstance(error, MissingTrustedAssetError):
        raise
else:
    raise AssertionError('unknown tag unexpectedly resolved')
"""
    environment = dict(os.environ, PYTHONPATH=str(project_root), NLTK_DATA=str(tmp_path / "nltk_data"))
    result = subprocess.run([sys.executable, "-c", code, str(script)],
                            cwd=tmp_path if outside_checkout else project_root,
                            env=environment, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
