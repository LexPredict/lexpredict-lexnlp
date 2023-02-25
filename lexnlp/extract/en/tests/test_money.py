#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Money unit tests for English.

This module implements unit tests for the money extraction functionality in English.

Todo:
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
from lexnlp.extract.en.money import get_money
from lexnlp.tests import lexnlp_tests
from unittest import TestCase


class MoneyTest(TestCase):

    def test_get_money_order(self):
        """
        At some moment there was a problem: get_money() was returning money in reversed order.
        This test is ensures the order is straight.
        :return:
        """
        text = ''' $96,844.00 per month ($31.00 per square foot per year), beginning on the date which is 90 days after 
        the Commencement Date and ending on the Expiration Date.'''
        actual = list(get_money(text, return_sources=False, float_digits=6))
        self.assertEqual(actual[0][0], 96844.0)

    def test_get_money_problem1(self):
        """
        Problem: it was returning 23.6 instead of 23.62 for such cases.
        :return:
        """
        text = '''Exercise Price per Share: 23.62'''
        actual = list(get_money(text, return_sources=False, float_digits=6))
        self.assertEqual(actual[0][0], Decimal('23.62'))


def test_get_money():
    """
    Test money extraction.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(
        func=get_money,
        return_sources=False,
        expected_data_converter=lambda expected: [
            (
                Decimal(amount) if amount else None,
                currency
            )
            for amount, currency in expected
        ]
    )


def test_get_money_source():
    """
    Test money extraction with source.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(
        func=get_money,
        return_sources=True,
        expected_data_converter=lambda expected: [
            (
                Decimal(amount) if amount else None,
                currency,
                source
            )
            for amount, currency, source in expected
            if amount or currency or source
        ]
    )
