#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Amount unit tests for English.

This module implements unit tests for the amount extraction functionality in English.

Todo:
    * More pathological and difficult cases
"""

# Imports
from nose.tools import assert_equal, assert_list_equal

from lexnlp.extract.en.amounts import get_amounts

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

EXAMPLE_AMOUNTS = [
    'total 34,567,890 documents',  # integer with comma
    'total 25,890.33 dollars',  # float with comma
    'total 2 million people',  # mixed number
    'total 2.035 billion tons of',  # mixed number with float
    'total twenty-five MILLION dollars',  # mixed upper-lower case

    'will cost 1/33',  # fraction
    'will cost 1/100',  # fraction N/100
    'will cost 25/100',  # fraction NN/100

    'THIRTY-SIX THOUSAND TWO-HUNDRED SIXTY-SIX AND 2/100',  # mixed written and decimal N/100
    'twenty-five and NO/100',  # No/100
    'total Seven Hundred Eighty and 87/100 Dollars ($780.87) per month',
    'one hundred AND five AND 25/100',  # AND inside written number
    'twenty-FIFTH day of month',  # nTH numbers
    'amount of RMB 200,000 (TWO HUNDRED THOUSAND YUAN) ',  # the same written/plain number
    'get .5 of total amount',  # number starting from dot
    'get .5 million',  # mixed number starting from dot
    'they need $25,400, 1 million people and 3.5 tons of sugar',  # multiple numbers in a string

    'three-tenths',  # fractions
    'one-twelfth',
    'ten ninety-ninths',
    'ten and one-third',
    'twenty one-hundredths',
    'twenty \n AND one-hundredths',
    '2 hundred and \none-thousandth',

    'a dozen months',  # dozen
    'twenty-two DOZEN \nand 1/100',  # dozen
    'two and \na HALF',  # half
    'Six and a HALF Billion',  # half inside number
    'one-quarter',  # quarter
    'five and three-quarters',  # written number and quarter
    '5 and three-quarters',

    'no number at the end of dONE word',  # no number
    'no number at the beginning of TENant as well',
    '5.3.1. Test Case.',  # check wrong number
    'word AND word',  # check AND without number
    '1/1/2010',
    """"There are 10 dogs.""",
    """There are fifteen cats.""",
    """I have 10,000 friends.""",
    "He has two thousand friends.",
    "They generated thirty-five million units.",
    "There are two hundred and thirty million ants here.",
    "nine hundred and ninety-nine bottles",
    """I found 27.5123 apples.""",
    """The aggregate Term Loan Commitment with respect to the Initial Term Loan of all Term Loan Lenders on
the Closing Date shall be $200,000,000.""",
    """There are FIFTY MILLION dollars.""",
    """There are 50 MILLION dollars.""",
    "There are five dogs and one cat.",
    "There are 10 people, five dogs and one cat.",
    "This string ends with the number 20",
    "This string ends with the number 20,000",
    "This string ends with the number 20,000,000",
    "This is not a 5.4.3. number",
]

RESULT = [
    [34567890.0],
    [25890.33],
    [2000000.0],
    [2035000000.0],
    [25000000],
    [0.0303],
    [0.01],
    [0.25],
    [36266.02],
    [25],
    [780.87, 780.87],
    [105.25],
    [25],
    [200000.0, 200000],
    [0.5],
    [500000.0],
    [25400.0, 1000000.0, 3.5],
    [0.3],
    [0.0833],
    [0.101],
    [10.3333],
    [0.21],
    [20.01],
    [200.001],
    [12],
    [264.01],
    [2.5],
    [6500000000.0],
    [0.25],
    [5.75],
    [5.75],
    [],
    [],
    [],
    [],
    [],
    [10.0],
    [15],
    [10000.0],
    [2000],
    [35000000],
    [230000000],
    [999],
    [27.5123],
    [200000000.0],
    [50000000],
    [50000000.0],
    [5, 1],
    [10.0, 5, 1],
    [20.0],
    [20000.0],
    [20000000.0],
    [],
]

RESULT_WITH_SOURCE = [
    [(34567890.0, '34,567,890')],
    [(25890.33, '25,890.33')],
    [(2000000.0, '2 million')],
    [(2035000000.0, '2.035 billion')],
    [(25000000, 'twenty-five MILLION')],
    [(0.0303, '1/33')],
    [(0.01, '1/100')],
    [(0.25, '25/100')],
    [(36266.02, 'THIRTY-SIX THOUSAND TWO-HUNDRED SIXTY-SIX AND 2/100')],
    [(25, 'twenty-five and NO/100')],
    [(780.87, 'Seven Hundred Eighty and 87/100'), (780.87, '780.87)')],
    [(105.25, 'one hundred AND five AND 25/100')],
    [(25, 'twenty-FIFTH')],
    [(200000.0, '200,000'), (200000, '(TWO HUNDRED THOUSAND')],
    [(0.5, '.5')],
    [(500000.0, '.5 million')],
    [(25400.0, '25,400,'), (1000000.0, '1 million'), (3.5, '3.5')],
    [(0.3, 'three-tenths')],
    [(0.0833, 'one-twelfth')],
    [(0.101, 'ten ninety-ninths')],
    [(10.3333, 'ten and one-third')],
    [(0.21, 'twenty one-hundredths')],
    [(20.01, 'twenty \n AND one-hundredths')],
    [(200.001, '2 hundred and \none-thousandth')],
    [(12, 'dozen')],
    [(264.01, 'twenty-two DOZEN \nand 1/100')],
    [(2.5, 'two and \na HALF')],
    [(6500000000.0, 'Six and a HALF Billion')],
    [(0.25, 'one-quarter')],
    [(5.75, 'five and three-quarters')],
    [(5.75, '5 and three-quarters')],
    [],
    [],
    [],
    [],
    [],
    [(10.0, '10')],
    [(15, 'fifteen')],
    [(10000.0, '10,000')],
    [(2000, 'two thousand')],
    [(35000000, 'thirty-five million')],
    [(230000000, 'two hundred and thirty million')],
    [(999, 'nine hundred and ninety-nine')],
    [(27.5123, '27.5123')],
    [(200000000.0, '200,000,000.')],
    [(50000000, 'FIFTY MILLION')],
    [(50000000.0, '50 MILLION')],
    [(5, 'five'), (1, 'and one')],
    [(10.0, '10'), (5, 'five'), (1, 'and one')],
    [(20.0, '20')],
    [(20000.0, '20,000')],
    [(20000000.0, '20,000,000')],
    [],
]

RESULT_NON_ROUND_FLOATS = [
    [34567890.0],
    [25890.33],
    [2000000.0],
    [2035000000.0000002],
    [25000000],
    [0.030303030303030304],
    [0.01],
    [0.25],
    [36266.02],
    [25],
    [780.87, 780.87],
    [105.25],
    [25],
    [200000.0, 200000],
    [0.5],
    [500000.0],
    [25400.0, 1000000.0, 3.5],
    [0.3],
    [0.08333333333333333],
    [0.10101010101010101],
    [10.333333333333334],
    [0.21],
    [20.01],
    [200.001],
    [12],
    [264.01],
    [2.5],
    [6500000000.0],
    [0.25],
    [5.75],
    [5.75],
    [],
    [],
    [],
    [],
    [],
    [10.0],
    [15],
    [10000.0],
    [2000],
    [35000000],
    [230000000],
    [999],
    [27.5123],
    [200000000.0],
    [50000000],
    [50000000.0],
    [5, 1],
    [10.0, 5, 1],
    [20.0],
    [20000.0],
    [20000000.0],
    [],
]


def test_get_amount():
    """
    Test default get amount behavior.
    :return:
    """
    i = 0
    for text, res in zip(EXAMPLE_AMOUNTS, RESULT):
        print("Example {i}: {t}...".format(i=i, t=text[:40]))
        assert_equal(get_amounts(text, return_sources=False), res)
        i += 1


def test_get_amount_source():
    """
    Test get amount behavior with source return.
    :return:
    """
    i = 0
    for text, res in zip(EXAMPLE_AMOUNTS, RESULT_WITH_SOURCE):
        print("Example {i}: {t}...".format(i=i, t=text[:40]))
        assert_list_equal(get_amounts(text, return_sources=True), res)
        i += 1


def test_get_amount_non_round_float():
    """
    Test get amount behavior with source return.
    :return:
    """
    i = 0
    for text, res in zip(EXAMPLE_AMOUNTS, RESULT_NON_ROUND_FLOATS):
        print("Example {i}: {t}...".format(i=i, t=text[:40]))
        assert_list_equal(get_amounts(text, return_sources=False, float_digits=None), res)
        i += 1


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

    for _ in get_amounts(text):
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
    for _ in get_amounts(text):
        continue
