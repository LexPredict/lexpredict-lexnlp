#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Percent unit tests for English.

This module implements unit tests for the percent extraction functionality in English.

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
from lexnlp.extract.en.percents import get_percents
from lexnlp.tests import lexnlp_tests


def test_get_percents():
    """
    Test default get percent behavior.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(
        func=get_percents,
        return_sources=False,
        expected_data_converter=lambda expected: [
            (
                unit,
                Decimal(value_units) if value_units else None,
                Decimal(value_decimal) if value_decimal else None,
            )
            for unit, value_units, value_decimal in expected
            if unit or value_units or value_decimal
        ]
    )


def test_get_percents_source():
    """
    Test get percent behavior with source return.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(
        func=get_percents,
        return_sources=True,
        expected_data_converter=lambda expected: [
            (
                unit,
                Decimal(value_units) if value_units else None,
                Decimal(value_decimal) if value_decimal else None,
                source,
            )
            for unit, value_units, value_decimal, source in expected
            if unit or value_units or value_decimal or source
        ]
    )
