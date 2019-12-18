#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Ratio unit tests for English.

This module implements unit tests for the ratio extraction functionality in English.

Todo:
    * Better testing for exact test in return sources
    * More pathological and difficult cases
"""

# Imports

from lexnlp.extract.en.ratios import get_ratios
from lexnlp.tests import lexnlp_tests

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def test_get_ratios():
    """
    Test ratio extraction.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(get_ratios, return_sources=False,
                                                   expected_data_converter=lambda expected:
                                                   [(float(numerator) if numerator else None,
                                                     float(consequent) if consequent else None,
                                                     float(decimal) if decimal else None)
                                                    for numerator, consequent, decimal in expected])


def test_get_ratios_source():
    """
    Test ratio extraction with source.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(get_ratios, return_sources=True,
                                                   expected_data_converter=lambda expected:
                                                   [(float(numerator) if numerator else None,
                                                     float(consequent) if consequent else None,
                                                     float(decimal) if decimal else None,
                                                     source)
                                                    for numerator, consequent, decimal, source in expected])
