__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

import pytest


def test_collect_samples_uses_every_canonical_member_when_cap_is_zero(tmp_path):
    import io
    import tarfile

    from lexnlp.extract.en.contracts import runtime_model

    archive_path = tmp_path / "corpus.tar"
    expected = [
        ("CONTRACT_TYPES/A/z.txt", "first"),
        ("CONTRACT_TYPES/A/a.txt", "second"),
        ("CONTRACT_TYPES/A/m.txt", "third"),
        ("CONTRACT_TYPES/B/b.txt", "fourth"),
    ]
    with tarfile.open(archive_path, "w") as archive:
        for name, text in expected:
            payload = text.encode()
            member = tarfile.TarInfo(name)
            member.size = len(payload)
            archive.addfile(member, io.BytesIO(payload))

    first = runtime_model.collect_contract_type_samples(
        archive_path,
        max_docs_per_label=0,
        head_character_n=100,
    )
    second = runtime_model.collect_contract_type_samples(
        archive_path,
        max_docs_per_label=0,
        head_character_n=100,
    )

    assert first == second
    assert first == (
        ["first", "second", "third", "fourth"],
        ["A", "A", "A", "B"],
        {"A": 3, "B": 1},
    )


def test_collect_samples_applies_positive_per_label_cap(tmp_path):
    import io
    import tarfile

    from lexnlp.extract.en.contracts import runtime_model

    archive_path = tmp_path / "corpus.tar"
    with tarfile.open(archive_path, "w") as archive:
        for index in range(3):
            payload = f"sample-{index}".encode()
            member = tarfile.TarInfo(f"CONTRACT_TYPES/A/{index}.txt")
            member.size = len(payload)
            archive.addfile(member, io.BytesIO(payload))
        payload = b"other"
        member = tarfile.TarInfo("CONTRACT_TYPES/B/0.txt")
        member.size = len(payload)
        archive.addfile(member, io.BytesIO(payload))

    texts, labels, counts = runtime_model.collect_contract_type_samples(
        archive_path,
        max_docs_per_label=2,
        head_character_n=100,
    )

    assert texts == ["sample-0", "sample-1", "other"]
    assert labels == ["A", "A", "B"]
    assert counts == {"A": 2, "B": 1}


def test_write_pipeline_reuses_only_a_valid_existing_artifact(monkeypatch, tmp_path):
    from lexnlp.extract.en.contracts import runtime_model
    from lexnlp.ml import catalog

    monkeypatch.setattr(catalog, "CATALOG", tmp_path)
    destination = runtime_model.write_pipeline_to_catalog(
        pipeline={"version": 1},
        target_tag="pipeline/test/0.1",
        force=True,
    )
    original_bytes = destination.read_bytes()

    reused = runtime_model.write_pipeline_to_catalog(
        pipeline={"version": 2},
        target_tag="pipeline/test/0.1",
        force=False,
    )

    assert reused == destination
    assert destination.read_bytes() == original_bytes


def test_write_pipeline_atomically_repairs_a_corrupt_existing_artifact(
    monkeypatch,
    tmp_path,
):
    from lexnlp.extract.en.contracts import runtime_model
    from lexnlp.ml import catalog
    from lexnlp.utils.unpickler import load_sklearn_model

    monkeypatch.setattr(catalog, "CATALOG", tmp_path)
    destination = tmp_path / "pipeline/test/0.1" / runtime_model.CONTRACT_TYPE_MODEL_FILENAME
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"truncated pickle")

    repaired = runtime_model.write_pipeline_to_catalog(
        pipeline={"version": 2},
        target_tag="pipeline/test/0.1",
        force=False,
    )

    assert repaired == destination
    with repaired.open("rb") as model_file:
        assert load_sklearn_model(model_file) == {"version": 2}
    assert not list(destination.parent.glob(f".{destination.name}.*.tmp"))


def test_ensure_runtime_contract_type_model_force_trains(monkeypatch, tmp_path):
    """
    Regression test: force=True should bypass reusing/downloading the target tag and
    retrain + overwrite the runtime model.
    """
    from lexnlp.extract.en.contracts import runtime_model
    from lexnlp.ml import catalog

    calls = []

    def ensure_tag_downloaded(tag: str):
        calls.append(("ensure_tag_downloaded", tag))
        if tag == runtime_model.RUNTIME_CONTRACT_TYPE_TAG:
            raise AssertionError("force=True should not attempt to download the target tag")
        return tmp_path / "corpus.tar.xz"

    def collect_samples(_archive_path, *, max_docs_per_label: int, head_character_n: int):
        calls.append(("collect_contract_type_samples", max_docs_per_label, head_character_n))
        return ["doc-a", "doc-b"], ["A", "B"], {"A": 1, "B": 1}

    def train_pipeline(texts, labels, *, random_state: int, max_features: int):
        calls.append(
            (
                "train_contract_type_pipeline",
                len(texts),
                len(labels),
                random_state,
                max_features,
            )
        )
        return object()

    def write_pipeline(*, pipeline, target_tag: str, force: bool):
        calls.append(("write_pipeline_to_catalog", target_tag, force))
        destination = tmp_path / "pipeline_contract_type_classifier.cloudpickle"
        destination.write_bytes(b"dummy")
        return destination

    monkeypatch.setattr(catalog, "CATALOG", tmp_path / "catalog")
    catalog.invalidate_catalog_cache()
    monkeypatch.setattr(runtime_model, "ensure_tag_downloaded", ensure_tag_downloaded)
    monkeypatch.setattr(runtime_model, "collect_contract_type_samples", collect_samples)
    monkeypatch.setattr(runtime_model, "train_contract_type_pipeline", train_pipeline)
    monkeypatch.setattr(runtime_model, "write_pipeline_to_catalog", write_pipeline)

    result = runtime_model.ensure_runtime_contract_type_model(
        target_tag=runtime_model.RUNTIME_CONTRACT_TYPE_TAG,
        force=True,
    )

    assert result == tmp_path / "pipeline_contract_type_classifier.cloudpickle"
    assert (
        "write_pipeline_to_catalog",
        catalog.get_local_candidate_tag(runtime_model.RUNTIME_CONTRACT_TYPE_TAG),
        True,
    ) in calls
    assert ("train_contract_type_pipeline", 2, 2, 7, 75_000) in calls
    catalog.invalidate_catalog_cache()


def test_release_tag_lookup_aliases_physically_separate_local_candidate(
    monkeypatch,
    tmp_path,
):
    from lexnlp.ml import catalog

    release_tag = "pipeline/is-contract/0.2"
    local_tag = catalog.get_local_candidate_tag(release_tag)
    local_path = tmp_path / local_tag / "model.cloudpickle"
    local_path.parent.mkdir(parents=True)
    local_path.write_bytes(b"local candidate")

    monkeypatch.setattr(catalog, "CATALOG", tmp_path)
    catalog.invalidate_catalog_cache()

    with pytest.raises(FileNotFoundError, match="exact tag"):
        catalog.get_exact_path_from_catalog(release_tag)
    assert catalog.get_path_from_catalog(release_tag) == local_path
    assert not (tmp_path / release_tag).exists()
    catalog.invalidate_catalog_cache()


def test_manifest_pinned_pipeline_write_rejects_non_manifest_bytes(
    monkeypatch,
    tmp_path,
):
    from lexnlp.extract.en.contracts import runtime_model
    from lexnlp.ml import catalog
    from lexnlp.ml.catalog import download

    monkeypatch.setattr(catalog, "CATALOG", tmp_path)
    catalog.invalidate_catalog_cache()

    with pytest.raises(download.ChecksumError, match="size|SHA-256"):
        runtime_model.write_pipeline_to_catalog(
            pipeline={"locally": "trained"},
            target_tag=runtime_model.RUNTIME_CONTRACT_TYPE_TAG,
            force=True,
        )

    release_dir = tmp_path / runtime_model.RUNTIME_CONTRACT_TYPE_TAG
    assert not (
        release_dir / runtime_model.CONTRACT_TYPE_MODEL_FILENAME
    ).exists()
    assert not list(release_dir.glob(".*.tmp"))
    catalog.invalidate_catalog_cache()


def test_runtime_model_reuses_private_candidate_without_release_directory(
    monkeypatch,
    tmp_path,
):
    from lexnlp.extract.en.contracts import runtime_model
    from lexnlp.ml import catalog
    from lexnlp.ml.catalog import download

    monkeypatch.setattr(catalog, "CATALOG", tmp_path)
    catalog.invalidate_catalog_cache()
    local_tag = catalog.get_local_candidate_tag(
        runtime_model.RUNTIME_CONTRACT_TYPE_TAG
    )
    local_path = runtime_model.write_pipeline_to_catalog(
        pipeline={"candidate": 1},
        target_tag=local_tag,
        force=True,
    )

    monkeypatch.setattr(
        download,
        "download_github_release_to_path",
        lambda *_args, **_kwargs: pytest.fail(
            "a valid private candidate should be reused"
        ),
    )

    assert runtime_model.ensure_runtime_contract_type_model() == local_path
    assert not (tmp_path / runtime_model.RUNTIME_CONTRACT_TYPE_TAG).exists()
    catalog.invalidate_catalog_cache()


def test_runtime_model_does_not_train_after_release_checksum_failure(
    monkeypatch,
    tmp_path,
):
    from lexnlp.extract.en.contracts import runtime_model
    from lexnlp.ml import catalog
    from lexnlp.ml.catalog import download

    monkeypatch.setattr(catalog, "CATALOG", tmp_path)
    catalog.invalidate_catalog_cache()
    monkeypatch.setattr(
        download,
        "download_github_release_to_path",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            download.ChecksumError("release checksum mismatch")
        ),
    )
    monkeypatch.setattr(
        runtime_model,
        "ensure_tag_downloaded",
        lambda _tag: pytest.fail("trust failure must not trigger training"),
    )

    with pytest.raises(download.ChecksumError, match="checksum mismatch"):
        runtime_model.ensure_runtime_contract_type_model()
    catalog.invalidate_catalog_cache()
