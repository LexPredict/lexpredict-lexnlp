#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""PII unit tests for English.

This module implements unit tests for the PII extraction functionality in English.

Todo:
    * Better testing for exact test in return sources
    * Add more PII examples
"""
from lexnlp.extract.en.pii import get_ssns, get_us_phones, get_pii
from lexnlp.tests import lexnlp_tests

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.8"
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
    lexnlp_tests.test_extraction_func_on_test_data(get_ssns, return_sources=False)


def test_ssn_list_source():
    """
    Test SSN detection.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(get_ssns, return_sources=True)


def test_us_phone_list():
    """
    Test US phone number detection.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(get_us_phones, return_sources=False)


def test_us_phone_list_source():
    """
    Test US phone number detection.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(get_us_phones, return_sources=True)


def test_pii_list():
    lexnlp_tests.test_extraction_func_on_test_data(get_pii, return_sources=False)


def test_pii_list_source():
    lexnlp_tests.test_extraction_func_on_test_data(get_pii, return_sources=True)
