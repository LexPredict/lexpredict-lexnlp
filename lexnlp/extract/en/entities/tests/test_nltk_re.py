#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Unit tests for the NLTK regular expression entity extraction methods.

This module implements unit tests for the named entity extraction functionality in English based on the
NLTK POS-tagging and (fuzzy) chunking methods.

Todo:
    * Better testing for exact test in return sources
    * More pathological and difficult cases
"""

from nose.tools import assert_list_equal

from lexnlp.extract.en.entities.nltk_re import get_companies, get_parties_as
from lexnlp.tests import lexnlp_tests

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# def test_companies_in_article():
#     """
#     Test get_companies default behavior.
#     :return:
#     """
#     lexnlp_tests.test_extraction_func_on_test_data(get_companies,
#                                                    expected_data_converter=lambda row: row[0],
#                                                    test_only_expected_in=True,
#                                                    use_article=True)


def test_company_article_regex():
    """
    Test company regular expressions.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(get_companies,
                                                   expected_data_converter=lambda row: row[0],
                                                   test_only_expected_in=True,
                                                   use_article=True,
                                                   detail_type=True)


def test_company_regex():
    """
    Test company regular expressions.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(get_companies,
                                                   expected_data_converter=lambda row: row[0],
                                                   test_only_expected_in=True,
                                                   use_article=False)


def test_company_as():
    """
    Text company as ... strings.
    :return:
    """
    # Check for empty text first
    actual = list(get_parties_as(''))
    expected = []
    assert_list_equal(actual, expected)

    lexnlp_tests.test_extraction_func_on_test_data(get_parties_as)
