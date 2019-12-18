#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Amount unit tests for English.

This module implements unit tests for the amount extraction functionality in English.

Todo:
    * More pathological and difficult cases
"""

# Imports

from lexnlp.extract.en.amounts import get_amounts
from lexnlp.tests import lexnlp_tests

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def test_get_amount():
    """
    Test default get amount behavior.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(get_amounts, return_sources=False,
                                                   expected_data_converter=lambda expected:
                                                   [float(amount) for amount in expected])


def test_get_amount_source():
    """
    Test get amount behavior with source return.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(get_amounts, return_sources=True,
                                                   expected_data_converter=lambda expected:
                                                   [(float(amount), source) for (amount, source) in expected])


def test_get_amount_non_round_float():
    """
    Test get amount behavior with source return.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(get_amounts, return_sources=False, float_digits=None,
                                                   expected_data_converter=lambda expected:
                                                   [float(amount) for amount in expected])


def test_error_case_1():
    """
    Test encountered error case.
    :return:
    """

    text = """55	                        "Term Loan Commitment" means, with respect to each Lender, the commitment,
if any, of such Lender to make a Term Loan hereunder in the amount set forth on Annex I to this Agreement or on 
Schedule 1 to the Assignment and Assumption pursuant to which such Lender assumed its Term Loan Commitment, as 
applicable, as the same may be (a) increased from time to time pursuant to Section 2.19 and (b) reduced or increased 
from time to time pursuant to assignments by or to such Lender pursuant to Section 10.04."""

    for _ in lexnlp_tests.benchmark_extraction_func(get_amounts, text):
        continue


def test_error_case_2():
    """
    Test encountered error case.
    :return:
    """
    text = """"Revolving Commitment Termination Date" shall mean the earliest of (i) May 11, 2021, (ii) the date on 
which the Revolving Commitments are terminated pursuant to Section 2.8 and (iii) the date on which all amounts 
outstanding under this Agreement have been declared or have automatically become due and payable (whether by 
acceleration or otherwise)."""
    for _ in lexnlp_tests.benchmark_extraction_func(get_amounts, text):
        continue
