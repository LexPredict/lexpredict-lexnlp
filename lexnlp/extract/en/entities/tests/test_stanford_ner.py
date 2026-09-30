#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Name unit tests for English.

This module implements unit tests for the name extraction functionality in English.

Todo:
    * Better testing for exact test in return sources
    * More pathological and difficult cases
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import pytest

from lexnlp import is_stanford_enabled
from lexnlp.tests import lexnlp_tests


class RecordingTagger:
    def __init__(self, labels):
        self.labels = labels
        self.calls = []

    def tag(self, tokens):
        tokens = list(tokens)
        self.calls.append(tokens)
        return [(token, self.labels.get(token, "O")) for token in tokens]


def test_stanford_ner_tags_each_sentence_once(monkeypatch):
    from lexnlp.extract.en.entities import stanford_ner

    sentences = [
        "Alice joined Acme.",
        "Bob moved to London.",
    ]
    tagger = RecordingTagger(
        {
            "Alice": "PERSON",
            "Acme": "ORGANIZATION",
            "Bob": "PERSON",
            "London": "LOCATION",
        }
    )
    monkeypatch.setattr(stanford_ner, "STANFORD_NER_TAGGER", tagger)
    monkeypatch.setattr(stanford_ner, "get_sentence_list", lambda _text: iter(sentences))
    monkeypatch.setattr(
        stanford_ner,
        "get_tokens_list",
        lambda sentence: sentence.rstrip(".").split(),
    )

    assert list(stanford_ner.get_persons("ignored", return_source=True)) == [
        ("Alice", sentences[0]),
        ("Bob", sentences[1]),
    ]
    assert tagger.calls == [
        ["Alice", "joined", "Acme"],
        ["Bob", "moved", "to", "London"],
    ]

    tagger.calls.clear()
    assert list(stanford_ner.get_organizations("ignored", return_source=True)) == [
        ("Acme", sentences[0]),
    ]
    assert tagger.calls == [
        ["Alice", "joined", "Acme"],
        ["Bob", "moved", "to", "London"],
    ]

    tagger.calls.clear()
    assert list(stanford_ner.get_locations("ignored", return_source=True)) == [
        ("London", sentences[1]),
    ]
    assert tagger.calls == [
        ["Alice", "joined", "Acme"],
        ["Bob", "moved", "to", "London"],
    ]


@pytest.mark.skipif(not is_stanford_enabled(), reason="Stanford is disabled.")  # skip-audit: issue=https://github.com/LexPredict/lexpredict-lexnlp/pull/80 expires=2030-01-01
def test_stanford_name_example_in():
    from lexnlp.extract.en.entities.stanford_ner import get_persons
    lexnlp_tests.test_extraction_func_on_test_data(get_persons,
                                                   expected_data_converter=lambda row: row[0],
                                                   test_only_expected_in=True)


@pytest.mark.skipif(not is_stanford_enabled(), reason="Stanford is disabled.")  # skip-audit: issue=https://github.com/LexPredict/lexpredict-lexnlp/pull/80 expires=2030-01-01
def test_stanford_org_example_in():
    from lexnlp.extract.en.entities.stanford_ner import get_organizations
    lexnlp_tests.test_extraction_func_on_test_data(get_organizations,
                                                   expected_data_converter=lambda row: row[0],
                                                   test_only_expected_in=True)


@pytest.mark.skipif(not is_stanford_enabled(), reason="Stanford is disabled.")  # skip-audit: issue=https://github.com/LexPredict/lexpredict-lexnlp/pull/80 expires=2030-01-01
def test_stanford_locations():
    """
    Test Stanford NER location extraction.
    :return:
    """
    from lexnlp.extract.en.entities.stanford_ner import get_locations
    lexnlp_tests.test_extraction_func_on_test_data(get_locations)
