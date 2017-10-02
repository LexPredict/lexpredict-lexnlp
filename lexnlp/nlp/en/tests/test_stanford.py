#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from lexnlp import enable_stanford, disable_stanford

# Nose imports
from nose.tools import assert_list_equal, with_setup

# Project imports
from lexnlp.nlp.en.stanford import get_tokens, get_verbs, get_nouns
from lexnlp.nlp.en.tests.test_tokens import EXAMPLE_TEXT_2, EXAMPLE_TEXT_2_TOKENS, EXAMPLE_TEXT_2_VERBS, \
    EXAMPLE_TEXT_2_VERB_LEMMAS

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def setup_module():
    """
    Setup environment pre-tests
    :return:
    """
    enable_stanford()


def teardown_module():
    """
    Setup environment post-tests.
    :return:
    """
    disable_stanford()


@with_setup(setup_module, teardown_module)
def test_stanford_token_example_2():
    tokens = get_tokens(EXAMPLE_TEXT_2)
    assert_list_equal(tokens, EXAMPLE_TEXT_2_TOKENS)


@with_setup(setup_module, teardown_module)
def test_stanford_token_example_2_lc():
    tokens = get_tokens(EXAMPLE_TEXT_2, lowercase=True)
    assert_list_equal(tokens, [t.lower() for t in EXAMPLE_TEXT_2_TOKENS])


@with_setup(setup_module, teardown_module)
def test_stanford_token_example_2_sw():
    from lexnlp.nlp.en.tokens import STOPWORDS

    tokens = get_tokens(EXAMPLE_TEXT_2, stopword=True)
    assert_list_equal(tokens, [t for t in EXAMPLE_TEXT_2_TOKENS if t.lower() not in STOPWORDS])


@with_setup(setup_module, teardown_module)
def test_stanford_token_example_2_lc_sw():
    from lexnlp.nlp.en.tokens import STOPWORDS

    tokens = get_tokens(EXAMPLE_TEXT_2, lowercase=True, stopword=True)
    assert_list_equal(tokens, [t.lower() for t in EXAMPLE_TEXT_2_TOKENS if t.lower() not in STOPWORDS])


@with_setup(setup_module, teardown_module)
def test_stanford_verbs_example_2():
    verbs = get_verbs(EXAMPLE_TEXT_2)
    assert_list_equal(verbs, EXAMPLE_TEXT_2_VERBS)


@with_setup(setup_module, teardown_module)
def test_stanford_verb_lemmas_example_2():
    verbs = get_verbs(EXAMPLE_TEXT_2, lemmatize=True)
    assert_list_equal(verbs, EXAMPLE_TEXT_2_VERB_LEMMAS)


@with_setup(setup_module, teardown_module)
def test_stanford_nouns_example_2():
    nouns = get_nouns(EXAMPLE_TEXT_2)
    assert_list_equal(nouns, ['Associated', 'General', 'Contractors', 'America'])


@with_setup(setup_module, teardown_module)
def test_stanford_noun_lemmas_example_2():
    nouns = get_nouns(EXAMPLE_TEXT_2, lemmatize=True)
    assert_list_equal(nouns, ['Associated', 'General', 'Contractors', 'America'])
