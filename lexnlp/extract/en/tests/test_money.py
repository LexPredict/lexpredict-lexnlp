#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Money unit tests for English.

This module implements unit tests for the money extraction functionality in English.

Todo:
    * More pathological and difficult cases
"""

# Imports

from lexnlp.extract.en.money import get_money
from lexnlp.tests import lexnlp_tests

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def test_get_money():
    """
    Test money extraction.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(get_money, return_sources=False,
                                                   expected_data_converter=lambda expected:
                                                   [(float(amount) if amount else None, currency) for amount, currency
                                                    in expected])


def test_get_money_source():
    """
    Test money extraction with source.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(get_money, return_sources=True,
                                                   expected_data_converter=lambda expected:
                                                   [(float(amount) if amount else None, currency, source)
                                                    for amount, currency, source in expected
                                                    if amount or currency or source])
