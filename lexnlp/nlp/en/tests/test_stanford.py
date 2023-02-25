#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import pytest
from nose.tools import with_setup

# Project imports
from lexnlp import is_stanford_enabled
from lexnlp.tests import lexnlp_tests


def setup_module():
    """
    Setup environment pre-tests
    :return:
    """
    # enable_stanford()


def teardown_module():
    """
    Setup environment post-tests.
    :return:
    """
    # disable_stanford()


@with_setup(setup_module, teardown_module)
@pytest.mark.skipif(not is_stanford_enabled(), reason="Stanford is disabled.")
def test_stanford_tokens():
    from lexnlp.nlp.en.stanford import get_tokens_list
    lexnlp_tests.test_extraction_func_on_test_data(get_tokens_list)


@with_setup(setup_module, teardown_module)
@pytest.mark.skipif(not is_stanford_enabled(), reason="Stanford is disabled.")
def test_stanford_tokens_lc():
    from lexnlp.nlp.en.stanford import get_tokens_list
    lexnlp_tests.test_extraction_func_on_test_data(get_tokens_list, lowercase=True)


@with_setup(setup_module, teardown_module)
@pytest.mark.skipif(not is_stanford_enabled(), reason="Stanford is disabled.")
def test_stanford_tokens_sw():
    from lexnlp.nlp.en.stanford import get_tokens_list
    lexnlp_tests.test_extraction_func_on_test_data(get_tokens_list, stopword=True)


@with_setup(setup_module, teardown_module)
@pytest.mark.skipif(not is_stanford_enabled(), reason="Stanford is disabled.")
def test_stanford_tokens_lc_sw():
    from lexnlp.nlp.en.stanford import get_tokens_list
    lexnlp_tests.test_extraction_func_on_test_data(get_tokens_list, lowercase=True, stopword=True)


@with_setup(setup_module, teardown_module)
@pytest.mark.skipif(not is_stanford_enabled(), reason="Stanford is disabled.")
def test_stanford_verbs():
    from lexnlp.nlp.en.stanford import get_verbs
    lexnlp_tests.test_extraction_func_on_test_data(get_verbs)


@with_setup(setup_module, teardown_module)
@pytest.mark.skipif(not is_stanford_enabled(), reason="Stanford is disabled.")
def test_stanford_verb_lemmas():
    from lexnlp.nlp.en.stanford import get_verbs
    lexnlp_tests.test_extraction_func_on_test_data(get_verbs, lemmatize=True)


@with_setup(setup_module, teardown_module)
@pytest.mark.skipif(not is_stanford_enabled(), reason="Stanford is disabled.")
def test_stanford_noun_lemmas():
    from lexnlp.nlp.en.stanford import get_nouns
    lexnlp_tests.test_extraction_func_on_test_data(get_nouns, lemmatize=True)


@with_setup(setup_module, teardown_module)
@pytest.mark.skipif(not is_stanford_enabled(), reason="Stanford is disabled.")
def test_stanford_nouns():
    from lexnlp.nlp.en.stanford import get_nouns
    lexnlp_tests.test_extraction_func_on_test_data(get_nouns)
