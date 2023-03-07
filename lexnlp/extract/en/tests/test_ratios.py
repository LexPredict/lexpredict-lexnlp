#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Ratio unit tests for English.

This module implements unit tests for the ratio extraction functionality in English.

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


# standard library imports
from decimal import Decimal

# LexNLP imports
from lexnlp.extract.en.ratios import get_ratios
from lexnlp.tests import lexnlp_tests


def test_get_ratios():
    """
    Test ratio extraction.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(
        func=get_ratios,
        return_sources=False,
        expected_data_converter=lambda expected: [
            (
                Decimal(numerator) if numerator else None,
                Decimal(consequent) if consequent else None,
                Decimal(decimal) if decimal else None
            )
            for numerator, consequent, decimal in expected
        ]
    )


def test_get_ratios_source():
    """
    Test ratio extraction with source.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(
        func=get_ratios,
        return_sources=True,
        expected_data_converter=lambda expected: [
            (
                Decimal(numerator) if numerator else None,
                Decimal(consequent) if consequent else None,
                Decimal(decimal) if decimal else None,
                source,
            )
            for numerator, consequent, decimal, source in expected
        ]
    )
