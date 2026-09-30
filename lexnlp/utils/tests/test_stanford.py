"""Stanford compatibility behavior independent of installed Java assets."""

from pathlib import Path
from subprocess import PIPE

import pytest

from lexnlp.utils import stanford


def _adapter(kind):
    cls = {
        "tokenizer": stanford.StanfordTokenizer,
        "pos": stanford.StanfordPOSTagger,
        "ner": stanford.StanfordNERTagger,
    }[kind]
    adapter = object.__new__(cls)
    adapter._encoding = "utf-8"
    adapter._stanford_jar = "verified-stanford.jar"
    adapter._stanford_model = "verified-model"
    adapter.java_options = "-mx1000m"
    if kind == "tokenizer":
        adapter._options_cmd = "americanize=True"
    return adapter


@pytest.mark.parametrize("kind", ["tokenizer", "pos", "ner"])
@pytest.mark.parametrize("output_type", [str, bytes])
def test_adapter_accepts_text_and_byte_output_and_removes_input(monkeypatch, kind, output_type):
    adapter = _adapter(kind)
    input_paths = []
    expected_input = "Café costs\n£2" if kind != "tokenizer" else "Café costs £2"
    output = {
        "tokenizer": "Café\ncosts\n£2\n",
        "pos": "Café_NN costs_VBZ\n£2_CD\n",
        "ner": "Café/ORGANIZATION costs/O £2/O\n",
    }[kind]

    def execute(command, **kwargs):
        assert kwargs == {
            "classpath": "verified-stanford.jar", "stdout": PIPE,
            "stderr": PIPE, "options": "-mx1000m",
        }
        path = command[-1] if kind == "tokenizer" else command[command.index("-textFile") + 1]
        input_paths.append(Path(path))
        assert Path(path).read_bytes() == expected_input.encode("utf-8")
        if kind == "tokenizer":
            assert command[0] == "edu.stanford.nlp.process.PTBTokenizer"
            assert "americanize=True" in command
        else:
            assert command[-2:] == ["-encoding", "utf-8"]
        return (output.encode("utf-8") if output_type is bytes else output), "diagnostic"

    monkeypatch.setattr(stanford, "java", execute)
    if kind == "tokenizer":
        assert adapter.tokenize(expected_input) == ["Café", "costs", "£2"]
    else:
        sentences = (iter(sentence) for sentence in [["Café", "costs"], ["£2"]])
        expected = (
            [[("Café", "NN"), ("costs", "VBZ")], [("£2", "CD")]]
            if kind == "pos" else [[("Café", "ORGANIZATION"), ("costs", "O")], [("£2", "O")]]
        )
        assert adapter.tag_sents(sentences) == expected
    assert len(input_paths) == 1
    assert not input_paths[0].exists()


@pytest.mark.parametrize("kind", ["tokenizer", "pos", "ner"])
def test_java_error_is_preserved_and_input_removed(monkeypatch, kind):
    adapter = _adapter(kind)
    paths = []

    def execute(command, **kwargs):
        path = command[-1] if kind == "tokenizer" else command[command.index("-textFile") + 1]
        paths.append(Path(path))
        assert paths[-1].exists()
        raise OSError("verified Java invocation failed")

    monkeypatch.setattr(stanford, "java", execute)
    with pytest.raises(OSError, match="verified Java invocation failed"):
        if kind == "tokenizer":
            adapter.tokenize("tokens")
        else:
            adapter.tag(["tokens"])
    assert paths and not paths[0].exists()


@pytest.mark.parametrize("kind", ["tokenizer", "pos", "ner"])
def test_invalid_byte_encoding_fails_and_input_removed(monkeypatch, kind):
    adapter = _adapter(kind)
    paths = []

    def execute(command, **kwargs):
        path = command[-1] if kind == "tokenizer" else command[command.index("-textFile") + 1]
        paths.append(Path(path))
        return b"\xff", b""

    monkeypatch.setattr(stanford, "java", execute)
    with pytest.raises(UnicodeDecodeError):
        if kind == "tokenizer":
            adapter.tokenize("tokens")
        else:
            adapter.tag(["tokens"])
    assert paths and not paths[0].exists()
