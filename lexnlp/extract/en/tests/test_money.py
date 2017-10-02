#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Money unit tests for English.

This module implements unit tests for the money extraction functionality in English.

Todo:
    * More pathological and difficult cases
"""

# Imports

from nose.tools import assert_set_equal

from lexnlp.extract.en.money import get_money

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

EXAMPLE_MONEY = ["the amount is $5,000,000.00 or less",
                 "Principal Amount:    20 Million Dollars ($20,000,000)",
                 "Principal Amount:    Seventy-five Million Dollars ($75,000,000)",
                 "$1,000,000 individually or $3,000,000 in the",
                 " to paragraph 7 below and expressed in euros per €1,000,000.",
                 """Credit Advances denominated in Dollars, $1,000,000 in respect of Revolving Credit Advances 
                 denominated in Sterling, £1,000,000, in respect of Revolving Credit Advances denominated in 
                 Swiss Francs, CHF1,000,000, in respect of Revolving Credit""",
                 "in the annual amount of RMB 200,000 (TWO HUNDRED THOUSAND CHINESE YUAN), payable",
                 "credit amounting to RMB 21 million yuan only ",
                 'one instance and ,Fifty Thousand and NO/100 Dollars ($50,000.00) ',
                 "There are 20,625.75 USD",
                 "There are $ 65.43 in the..",
                 "There are 10 dogs",
                 "The model number is X100 for your vacuum",
                 "There is no , money in the banana stand",
                 """Bank must be rated at least "A" by S&P and "A2" by Moody's.  No""",
                 "There are 5.4.3 dollars"
                 ]

RESULTS = [
    [(5000000.0, 'USD')],
    [(20000000.0, 'USD'), (20000000.0, 'USD')],
    [(75000000, 'USD'), (75000000.0, 'USD')],
    [(1000000.0, 'USD'), (3000000.0, 'USD')],
    [(1000000.0, 'EUR')],
    [(1000000.0, 'USD'), (1000000.0, 'GBP'), (1000000.0, 'CHF')],
    [(200000.0, 'CNY'), (200000, 'CNY')],
    [(21000000.0, 'CNY')],
    [(50000, 'USD'), (50000.0, 'USD')],
    [(20625.75, 'USD')],
    [(65.43, 'USD')],
    [],
    [],
    [],
    [],
    [],
]

RESULTS_SOURCE = [
    [(5000000.0, 'USD', '$5,000,000.00')],
    [(20000000.0, 'USD', '20 Million Dollar'),
     (20000000.0, 'USD', '$20,000,000)')],
    [(75000000, 'USD', 'Seventy-five Million Dollar'),
     (75000000.0, 'USD', '$75,000,000)')],
    [(1000000.0, 'USD', '$1,000,000'), (3000000.0, 'USD', '$3,000,000')],
    [(1000000.0, 'EUR', '€1,000,000.')],
    [(1000000.0, 'USD', '$1,000,000'), (1000000.0, 'GBP', '£1,000,000,'),
     (1000000.0, 'CHF', 'CHF1,000,000,')],
    [(200000.0, 'CNY', 'RMB 200,000 ('),
     (200000, 'CNY', 'TWO HUNDRED THOUSAND CHINESE YUAN')],
    [(21000000.0, 'CNY', 'RMB 21 million')],
    [(50000, 'USD', 'Fifty Thousand and NO/100 Dollar'),
     (50000.0, 'USD', '$50,000.00)')],
    [(20625.75, 'USD', '20,625.75 USD')],
    [(65.43, 'USD', '$ 65.43')],
    [],
    [],
    [],
    [],
    [],
]


def test_get_money():
    """
    Test money extraction.
    :return:
    """
    for i, example in enumerate(EXAMPLE_MONEY):
        print("Example {i}: {t}...".format(i=i, t=example[:40]))
        assert_set_equal(set(get_money(example, return_sources=False)),
                         set(RESULTS[i]))


def test_get_money_source():
    """
    Test money extraction with source.
    :return:
    """
    for i, example in enumerate(EXAMPLE_MONEY):
        print("Example {i}: {t}...".format(i=i, t=example[:40]))
        assert_set_equal(set(get_money(example, return_sources=False)),
                         set(RESULTS[i]))
