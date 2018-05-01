#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Imports
from nose.tools import assert_true, assert_equal

from lexnlp.nlp.en.transforms.characters import get_character_distribution
from lexnlp.nlp.en.transforms.tokens import get_token_distribution

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def test_character_distribution_example_1():
    """
    Test with example 1.
    :return:
    """
    distribution = get_character_distribution("abc")
    assert_true("a" in distribution)
    assert_equal(distribution["a"], 1)
    assert_true("b" in distribution)
    assert_equal(distribution["b"], 1)
    assert_true("c" in distribution)
    assert_equal(distribution["c"], 1)


def test_token_distribution_example_1():
    """
    Test with example 1.
    :return:
    """
    distribution = get_token_distribution("abc 123")
    assert_true("abc" in distribution)
    assert_equal(distribution["abc"], 1)
    assert_true("123" in distribution)
    assert_equal(distribution["123"], 1)
