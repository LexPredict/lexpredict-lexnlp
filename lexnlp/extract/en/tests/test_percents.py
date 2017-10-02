#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Percent unit tests for English.

This module implements unit tests for the percent extraction functionality in English.

Todo:
    * Better testing for exact test in return sources
    * More pathological and difficult cases
"""

# Imports

from nose.tools import assert_list_equal

from lexnlp.extract.en.percents import get_percents

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

EXAMPLE_PERCENTS = [
    " 30% or more plus \n3% and (ii) 12%.",
    "Percentage Interest:  3.67%, voting  rights with respect to ten percent (10%) or more",
    " eight and one third  percent  (8.33%)  and (iii) twenty-five percent (25%) of the",
    "Inc.  owning  less than one hundred percent",
    "twenty five percent",
    "twenty five basis points",
    "two hundred percentage points",
    "at least 50.1% of the membership interest",
    "A RATE PER ANNUM EQUAL TO LIBOR PLUS 400 BASIS POINTS, EFFECTIVE JANUARY 1, 2002",
    " an annual rate of 7.38%, which rate is equal to 200 basis points above the Bank's five-year",
    " power to vote more than 25% of the ",
    " plus four (4) percentage points for ",
    " he hot 5 points ",
    " comparable to the 2010 percentage salary increase ",
    " (2007) +/- [ * ]% ",
    "get $1,049 million and one percent",
]

RESULT = [
    [('%', 30.0, 0.3), ('%', 3.0, 0.03), ('%', 12.0, 0.12)],
    [('%', 3.67, 0.0367), ('percent', 10, 0.1), ('%', 10.0, 0.1)],
    [('percent', 8.3333, 0.0833), ('%', 8.33, 0.0833), ('percent', 25, 0.25), ('%', 25.0, 0.25)],
    [('percent', 100, 1.0)],
    [('percent', 25, 0.25)],
    [('basis points', 25, 0.0025)],
    [('percentage points', 200, 2.0)],
    [('%', 50.1, 0.501)],
    [('basis points', 400.0, 0.04)],
    [('%', 7.38, 0.0738), ('basis points', 200.0, 0.02)],
    [('%', 25.0, 0.25)],
    [('percentage points', 4.0, 0.04)],
    [],
    [],
    [],
    []
]

RESULT_WITH_SOURCE = [
    [('%', 30.0, 0.3, '30%'), ('%', 3.0, 0.03, '3%'), ('%', 12.0, 0.12, '12%')],
    [('%', 3.67, 0.0367, '3.67%'), ('percent', 10, 0.1, 'ten percent'),
     ('%', 10.0, 0.1, '10%')],
    [('percent', 8.3333, 0.0833, 'eight and one third  percent'),
     ('%', 8.33, 0.0833, '8.33%'),
     ('percent', 25, 0.25, 'twenty-five percent'),
     ('%', 25.0, 0.25, '25%')],
    [('percent', 100, 1.0, 'one hundred percent')],
    [('percent', 25, 0.25, 'twenty five percent')],
    [('basis points', 25, 0.0025, 'twenty five basis points')],
    [('percentage points', 200, 2.0, 'two hundred percentage points')],
    [('%', 50.1, 0.501, '50.1%')],
    [('basis points', 400.0, 0.04, '400 basis points')],
    [('%', 7.38, 0.0738, '7.38%'), ('basis points', 200.0, 0.02, '200 basis points')],
    [('%', 25.0, 0.25, '25%')],
    [('percentage points', 4.0, 0.04, '4) percentage points')],
    [],
    [],
    [],
    []
]


def test_get_percents():
    """
    Test default get percent behavior.
    :return:
    """
    i = 0
    for text, res in zip(EXAMPLE_PERCENTS, RESULT):
        print("Example {i}: {t}...".format(i=i, t=text[:40]))
        assert_list_equal(get_percents(text, return_sources=False), res)
        i += 1


def test_get_percents_source():
    """
    Test get percent behavior with source return.
    :return:
    """
    i = 0
    for text, res in zip(EXAMPLE_PERCENTS, RESULT_WITH_SOURCE):
        print("Example {i}: {t}...".format(i=i, t=text[:40]))
        assert_list_equal(get_percents(text, return_sources=True), res)
        i += 1
