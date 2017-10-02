#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""PII unit tests for English.

This module implements unit tests for the PII extraction functionality in English.

Todo:
    * Better testing for exact test in return sources
    * Add more PII examples
"""
from nose.tools import assert_equal

from lexnlp.extract.en.pii import get_ssns, get_us_phones, get_pii

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

SSN_EXAMPLE_LIST = [("Employee ID: 123-45-6789", ["123-45-6789"]),
                    ("There is no 12-34-45 SSN here.", []),
                    ("Some poor soul had 078-05-1120 once upon a time.", ["078-05-1120"])
                    ]

US_PHONE_EXAMPLE_LIST = [("Home Phone: (212) 212-2121", ["(212) 212-2121"]),
                         ]

PII_EXAMPLE_LIST = [("Employee ID: 078-05-1120",
                     [("ssn", "078-05-1120")]),
                    ("My ID is 078-05-1120 and my phone number is 212-212-2121",
                     [("ssn", "078-05-1120"), ("us_phone", "(212) 212-2121")]),
                    ]


def test_ssn_list():
    """
    Test SSN detection.
    :return:
    """
    for example, result in SSN_EXAMPLE_LIST:
        actual = list(get_ssns(example))
        assert_equal(actual, result)


def test_ssn_list_source():
    """
    Test SSN detection.
    :return:
    """
    for example, result in SSN_EXAMPLE_LIST:
        actual = list([s[0] for s in get_ssns(example, return_sources=True)])
        assert_equal(actual, result)


def test_us_phone_list():
    """
    Test US phone number detection.
    :return:
    """
    for example, result in US_PHONE_EXAMPLE_LIST:
        actual = list(get_us_phones(example))
        assert_equal(actual, result)


def test_us_phone_list_source():
    """
    Test US phone number detection.
    :return:
    """
    for example, result in US_PHONE_EXAMPLE_LIST:
        actual = list([p[0] for p in get_us_phones(example, return_sources=True)])
        assert_equal(actual, result)


def test_pii_list():
    for example, result in PII_EXAMPLE_LIST:
        actual = list(get_pii(example))
        assert_equal(actual, result)


def test_pii_list_source():
    for example, result in PII_EXAMPLE_LIST:
        actual = list([(p[0], p[1][0]) for p in get_pii(example, return_sources=True)])
        assert_equal(actual, result)
