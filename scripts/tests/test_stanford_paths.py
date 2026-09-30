"""Stanford bootstrap and runtime agree without changing NLTK trust roots."""

from __future__ import annotations

import hashlib
import io
import os
from pathlib import Path
import subprocess
import sys
import zipfile

import nltk.data
import pytest

from lexnlp.config import stanford
from scripts import bootstrap_assets


POS_COMPONENT = f"stanford-postagger-full-{stanford.STANFORD_VERSION}"
NER_COMPONENT = f"stanford-ner-{stanford.STANFORD_VERSION}"


class _Response(io.BytesIO):
    def __init__(self, payload: bytes, url: str):
        super().__init__(payload)
        self.url = url

    def geturl(self):
        return self.url


def _mock_verified_downloads(monkeypatch):
    assets = []
    responses = {}
    for component, filename in ((POS_COMPONENT, "stanford-postagger.jar"), (NER_COMPONENT, "stanford-ner.jar")):
        member_path = f"{component}/{filename}"
        member_payload = b"test runtime asset"
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr(member_path, member_payload)
        payload = buffer.getvalue()
        url = f"https://downloads.cs.stanford.edu/{component}.zip"
        assets.append(bootstrap_assets.StanfordArchive(
            filename=f"{component}.zip", url=url, size=len(payload),
            sha512=hashlib.sha512(payload).hexdigest(), root_directory=component,
            required_members=(bootstrap_assets.RequiredArchiveMember(
                path=member_path, size=len(member_payload),
                sha512=hashlib.sha512(member_payload).hexdigest(),
            ),),
        ))
        responses[url] = payload
    monkeypatch.setattr(bootstrap_assets, "STANFORD_DOWNLOADS", tuple(assets))
    monkeypatch.setattr(
        bootstrap_assets, "urlopen",
        lambda request, **kwargs: _Response(responses[request.full_url], request.full_url),
    )


def test_default_bootstrap_matches_runtime_under_existing_nltk_root(monkeypatch, tmp_path):
    data_root = tmp_path / "nltk-data"
    data_root.mkdir()
    monkeypatch.setattr(nltk.data, "path", [str(data_root)])
    _mock_verified_downloads(monkeypatch)
    before = list(nltk.data.path)
    args = bootstrap_assets.parse_args(["--stanford"])
    assert args.stanford_dir is None
    bootstrap_assets.run_selected_tasks(args)
    assert nltk.data.path == before
    assert bootstrap_assets._nltk_download_directory() == data_root
    assert stanford._resolve_stanford_path(POS_COMPONENT) == str(data_root / "stanford_nlp" / POS_COMPONENT)
    assert stanford._resolve_stanford_path(NER_COMPONENT) == str(data_root / "stanford_nlp" / NER_COMPONENT)
    assert (data_root / "stanford_nlp" / POS_COMPONENT / "stanford-postagger.jar").read_bytes() == b"test runtime asset"


def test_explicit_directory_uses_explicit_trust_root(monkeypatch, tmp_path):
    destination = tmp_path / "custom-stanford"
    monkeypatch.setattr(nltk.data, "path", [str(destination)])
    _mock_verified_downloads(monkeypatch)
    monkeypatch.setattr(
        bootstrap_assets, "_nltk_download_directory",
        lambda: pytest.fail("explicit Stanford destinations must not use the default"),
    )
    args = bootstrap_assets.parse_args(["--stanford", "--stanford-dir", str(destination)])
    bootstrap_assets.run_selected_tasks(args)
    assert nltk.data.path == [str(destination)]
    assert stanford._resolve_stanford_path(POS_COMPONENT) == str(destination / POS_COMPONENT)
    assert stanford._resolve_stanford_path(NER_COMPONENT) == str(destination / NER_COMPONENT)


def test_runtime_respects_nltk_root_order_before_legacy_paths(monkeypatch, tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    legacy = tmp_path / "legacy"
    for root in (first, second, legacy):
        (root / "stanford_nlp" / POS_COMPONENT).mkdir(parents=True)
    monkeypatch.setattr(nltk.data, "path", [str(first), str(second)])
    monkeypatch.setattr(stanford, "get_lib_path", lambda: str(legacy))
    assert stanford._resolve_stanford_path(POS_COMPONENT) == str(first / "stanford_nlp" / POS_COMPONENT)
    monkeypatch.setattr(nltk.data, "path", [str(second), str(first)])
    assert stanford._resolve_stanford_path(POS_COMPONENT) == str(second / "stanford_nlp" / POS_COMPONENT)


@pytest.mark.parametrize("present", ["system", "checkout", "neither"])
def test_legacy_system_and_checkout_fallbacks_remain(monkeypatch, tmp_path, present):
    system = tmp_path / "system-stanford"
    checkout = tmp_path / "checkout-libs"
    monkeypatch.setattr(nltk.data, "path", [])
    monkeypatch.setattr(stanford, "STANFORD_BASE_PATH", str(system))
    monkeypatch.setattr(stanford, "get_lib_path", lambda: str(checkout))
    if present == "system":
        (system / POS_COMPONENT).mkdir(parents=True)
        (checkout / "stanford_nlp" / POS_COMPONENT).mkdir(parents=True)
        expected = system / POS_COMPONENT
    else:
        expected = checkout / "stanford_nlp" / POS_COMPONENT
        if present == "checkout":
            expected.mkdir(parents=True)
    assert stanford._resolve_stanford_path(POS_COMPONENT) == str(expected)
    assert nltk.data.path == []


def test_default_dry_run_does_not_write_or_change_trust(monkeypatch, tmp_path):
    monkeypatch.setattr(nltk.data, "path", [str(tmp_path)])
    monkeypatch.setattr(
        bootstrap_assets, "urlopen",
        lambda *args, **kwargs: pytest.fail("dry run must not contact the network"),
    )
    bootstrap_assets.run_selected_tasks(bootstrap_assets.parse_args(["--stanford", "--dry-run"]))
    assert list(tmp_path.iterdir()) == []
    assert nltk.data.path == [str(tmp_path)]


def test_runtime_reads_multiple_nltk_data_roots_in_fresh_process(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    (first / "stanford_nlp" / POS_COMPONENT).mkdir(parents=True)
    (second / "stanford_nlp" / NER_COMPONENT).mkdir(parents=True)
    environment = dict(os.environ)
    environment["NLTK_DATA"] = os.pathsep.join((str(first), str(second)))
    repository_root = Path(__file__).resolve().parents[2]
    environment["PYTHONPATH"] = str(repository_root)
    result = subprocess.run(
        [sys.executable, "-c", (
            "from lexnlp.config.stanford import STANFORD_POS_PATH, STANFORD_NER_PATH; "
            "print(STANFORD_POS_PATH); print(STANFORD_NER_PATH)"
        )], env=environment, cwd=repository_root, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [
        str(first / "stanford_nlp" / POS_COMPONENT), str(second / "stanford_nlp" / NER_COMPONENT),
    ]
