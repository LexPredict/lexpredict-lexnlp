#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Imports

from nltk.corpus import wordnet
from nose.tools import assert_list_equal, nottest

from lexnlp.nlp.en.segments.sentences import get_sentence_list
from lexnlp.nlp.en.tokens import get_adjectives, get_adverbs, get_lemmas, get_lemma_list, get_nouns,\
    get_stem_list, get_tokens, get_token_list, get_verbs, get_wordnet_pos
from lexnlp.tests import lexnlp_tests

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


@nottest
def run_sentence_token_gen_test(text, result, lowercase=False, stopword=False):
    """
    Base test method to run against text with given results.
    """
    # Get list from text
    sentence_list = get_sentence_list(text)

    # Check length first
    assert len(sentence_list) == len(result)

    # Check each sentence matches
    for i in range(len(sentence_list)):
        tokens = list(lexnlp_tests.benchmark_extraction_func(get_tokens,
                                                             sentence_list[i], lowercase=lowercase, stopword=stopword))
        assert_list_equal(tokens, result[i])


@nottest
def run_sentence_token_test(text, result, lowercase=False, stopword=False):
    """
    Base test method to run against text with given results.
    """
    # Get list from text
    sentence_list = get_sentence_list(text)

    # Check length first
    assert len(sentence_list) == len(result)

    # Check each sentence matches
    for i in range(len(sentence_list)):
        tokens = lexnlp_tests.benchmark_extraction_func(get_token_list,
                                                        sentence_list[i], lowercase=lowercase, stopword=stopword)
        assert_list_equal(tokens, result[i])


def test_token_gen_example_1():
    run_sentence_token_gen_test("This is a test.", [["This", "is", "a", "test", "."]])


def test_token_gen_example_1_lc():
    run_sentence_token_gen_test("This is a test.", [["this", "is", "a", "test", "."]], lowercase=True)


def test_token_gen_example_1_sw():
    run_sentence_token_gen_test("This is a Test.", [["Test", "."]], stopword=True)


def test_token_example_1():
    run_sentence_token_test("This is a test.", [["This", "is", "a", "test", "."]])


def test_token_example_1_lc():
    run_sentence_token_test("This is a test.", [["this", "is", "a", "test", "."]], lowercase=True)


def test_stems():
    lexnlp_tests.test_extraction_func_on_test_data(get_stem_list,
                                                   expected_data_converter=lambda stems:
                                                         list(stem.lower() for stem in stems) if stems else None)


def test_stems_lowercase():
    lexnlp_tests.test_extraction_func_on_test_data(get_stem_list, lowercase=True)


def test_stems_lowercase_no_stopwords():
    lexnlp_tests.test_extraction_func_on_test_data(get_stem_list, stopword=True)


def test_wordnet_pos():
    # Import and setup map
    treebank_pos_map = {"JJ": wordnet.ADJ,
                        "JJR": wordnet.ADJ,
                        "JJS": wordnet.ADJ,
                        "VB": wordnet.VERB,
                        "VBD": wordnet.VERB,
                        "VBN": wordnet.VERB,
                        "NN": wordnet.NOUN,
                        "NNP": wordnet.NOUN,
                        "NNPS": wordnet.NOUN,
                        "RB": wordnet.ADV,
                        "RBR": wordnet.ADV
                        }

    # Check function output against map
    for k in treebank_pos_map:
        assert get_wordnet_pos(k) == treebank_pos_map[k]


def test_lemmas():
    lexnlp_tests.test_extraction_func_on_test_data(get_lemma_list)
    lexnlp_tests.test_extraction_func_on_test_data(get_lemmas)


def test_lemmas_lc():
    # Snowball returns lowercase always
    lexnlp_tests.test_extraction_func_on_test_data(get_lemma_list, lowercase=True)
    lexnlp_tests.test_extraction_func_on_test_data(get_lemmas, lowercase=True)


def test_lemmas_sw():
    lexnlp_tests.test_extraction_func_on_test_data(get_lemma_list, stopword=True)
    lexnlp_tests.test_extraction_func_on_test_data(get_lemmas, stopword=True)


def test_lemmas_lc_sw():
    lexnlp_tests.test_extraction_func_on_test_data(get_lemma_list, lowercase=True, stopword=True)
    lexnlp_tests.test_extraction_func_on_test_data(get_lemmas, lowercase=True, stopword=True)


def test_verbs():
    lexnlp_tests.test_extraction_func_on_test_data(get_verbs)


def test_verb_lemmas():
    lexnlp_tests.test_extraction_func_on_test_data(get_verbs, lemmatize=True)


def test_nouns():
    lexnlp_tests.test_extraction_func_on_test_data(get_nouns)


def test_nouns_lemma():
    lexnlp_tests.test_extraction_func_on_test_data(get_nouns, lemmatize=True)


def test_adjectives():
    lexnlp_tests.test_extraction_func_on_test_data(get_adjectives)


def test_adjectives_lemma():
    lexnlp_tests.test_extraction_func_on_test_data(get_adjectives, lemmatize=True)


def test_adverbs():
    lexnlp_tests.test_extraction_func_on_test_data(get_adverbs)


def test_adverbs_lemma():
    lexnlp_tests.test_extraction_func_on_test_data(get_adverbs, lemmatize=True)
