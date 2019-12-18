#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Percent unit tests for English.

This module implements unit tests for the percent extraction functionality in English.

Todo:
    * Better testing for exact test in return sources
    * More pathological and difficult cases
"""

# Imports

from lexnlp.extract.en.percents import get_percents
from lexnlp.tests import lexnlp_tests

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def test_get_percents():
    """
    Test default get percent behavior.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(get_percents, return_sources=False,
                                                   expected_data_converter=lambda expected:
                                                   [(unit,
                                                     float(value_units) if value_units else None,
                                                     float(value_decimal) if value_decimal else None)
                                                    for unit, value_units, value_decimal in expected
                                                    if unit or value_units or value_decimal])


def test_get_percents_source():
    """
    Test get percent behavior with source return.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(get_percents, return_sources=True,
                                                   expected_data_converter=lambda expected:
                                                   [(unit,
                                                     float(value_units) if value_units else None,
                                                     float(value_decimal) if value_decimal else None,
                                                     source)
                                                    for unit, value_units, value_decimal, source in expected
                                                    if unit or value_units or value_decimal or source])
