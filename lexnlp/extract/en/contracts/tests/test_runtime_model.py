__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def test_ensure_runtime_contract_type_model_force_trains(monkeypatch, tmp_path):
    """
    Regression test: force=True should bypass reusing/downloading the target tag and
    retrain + overwrite the runtime model.
    """
    from lexnlp.extract.en.contracts import runtime_model

    calls = []

    def ensure_tag_downloaded(tag: str):
        calls.append(("ensure_tag_downloaded", tag))
        if tag == runtime_model.RUNTIME_CONTRACT_TYPE_TAG:
            raise AssertionError("force=True should not attempt to download the target tag")
        return tmp_path / "corpus.tar.xz"

    def collect_samples(_archive_path, *, max_docs_per_label: int, head_character_n: int):
        calls.append(("collect_contract_type_samples", max_docs_per_label, head_character_n))
        return ["doc-a", "doc-b"], ["A", "B"], {"A": 1, "B": 1}

    def train_pipeline(texts, labels, *, random_state: int):
        calls.append(("train_contract_type_pipeline", len(texts), len(labels), random_state))
        return object()

    def write_pipeline(*, pipeline, target_tag: str, force: bool):
        calls.append(("write_pipeline_to_catalog", target_tag, force))
        destination = tmp_path / "pipeline_contract_type_classifier.cloudpickle"
        destination.write_bytes(b"dummy")
        return destination

    monkeypatch.setattr(runtime_model, "ensure_tag_downloaded", ensure_tag_downloaded)
    monkeypatch.setattr(runtime_model, "collect_contract_type_samples", collect_samples)
    monkeypatch.setattr(runtime_model, "train_contract_type_pipeline", train_pipeline)
    monkeypatch.setattr(runtime_model, "write_pipeline_to_catalog", write_pipeline)

    import lexnlp.ml.catalog

    def get_path_from_catalog(_tag: str):
        raise AssertionError("force=True should not consult the existing catalog path")

    monkeypatch.setattr(lexnlp.ml.catalog, "get_path_from_catalog", get_path_from_catalog)

    result = runtime_model.ensure_runtime_contract_type_model(
        target_tag=runtime_model.RUNTIME_CONTRACT_TYPE_TAG,
        force=True,
    )

    assert result == tmp_path / "pipeline_contract_type_classifier.cloudpickle"
    assert ("write_pipeline_to_catalog", runtime_model.RUNTIME_CONTRACT_TYPE_TAG, True) in calls

