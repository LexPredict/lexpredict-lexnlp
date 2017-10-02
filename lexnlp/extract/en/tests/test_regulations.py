#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Regulation unit tests for English.

This module implements unit tests for the regulation extraction functionality in English.

Todo:
    * Better testing for exact test in return sources
    * More pathological and difficult cases
"""

# Imports

from nose.tools import assert_list_equal

from lexnlp.extract.en.regulations import get_regulations

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

TEST_DATA = [
    ("test 55 C.F.R. 77 code",
     [('Code of Federal Regulations', '55 CFR 77')],
     [('Code of Federal Regulations', '55 CFR 77', '55 C.F.R. 77')],
     [{'regulation_code': '55 CFR 77',
       'regulation_type': 'Code of Federal Regulations'}],
     [{'regulation_code': '55 CFR 77',
       'regulation_str': '55 C.F.R. 77',
       'regulation_type': 'Code of Federal Regulations'}]),

    ("test 55  CFR  77a-22B code",
     [('Code of Federal Regulations', '55 CFR 77a-22B')],
     [('Code of Federal Regulations', '55 CFR 77a-22B', '55  CFR  77a-22B')],
     [{'regulation_code': '55 CFR 77a-22B',
       'regulation_type': 'Code of Federal Regulations'}],
     [{'regulation_code': '55 CFR 77a-22B',
       'regulation_str': '55  CFR  77a-22B',
       'regulation_type': 'Code of Federal Regulations'}]),

    ("test 123 U.S.C \n456, code",
     [('United States Code', '123 USC 456')],
     [('United States Code', '123 USC 456', '123 U.S.C \n456')],
     [{'regulation_code': '123 USC 456', 'regulation_type': 'United States Code'}],
     [{'regulation_code': '123 USC 456',
       'regulation_str': '123 U.S.C \n456',
       'regulation_type': 'United States Code'}]),

    # test paragraph
    ("test 123 U.S.C § 456, code",
     [('United States Code', '123 USC § 456')],
     [('United States Code', '123 USC § 456', '123 U.S.C § 456')],
     [{'regulation_code': '123 USC § 456',
       'regulation_type': 'United States Code'}],
     [{'regulation_code': '123 USC § 456',
       'regulation_str': '123 U.S.C § 456',
       'regulation_type': 'United States Code'}]),

    # test Section
    ("test 123 U.S.C Section 456, code",
     [('United States Code', '123 USC Section 456')],
     [('United States Code', '123 USC Section 456', '123 U.S.C Section 456')],
     [{'regulation_code': '123 USC Section 456',
       'regulation_type': 'United States Code'}],
     [{'regulation_code': '123 USC Section 456',
       'regulation_str': '123 U.S.C Section 456',
       'regulation_type': 'United States Code'}]),

    # test substitute Sec. with Section
    ("test 123 U.S.C Sec. 456, code",
     [('United States Code', '123 USC Section 456')],
     [('United States Code', '123 USC Section 456', '123 U.S.C Sec. 456')],
     [{'regulation_code': '123 USC Section 456',
       'regulation_type': 'United States Code'}],
     [{'regulation_code': '123 USC Section 456',
       'regulation_str': '123 U.S.C Sec. 456',
       'regulation_type': 'United States Code'}]),

    ("test Public Law No.   123-456 code",
     [('Public Law', 'Public Law No. 123-456')],
     [('Public Law', 'Public Law No. 123-456', 'Public Law No.   123-456')],
     [{'regulation_code': 'Public Law No. 123-456',
       'regulation_type': 'Public Law'}],
     [{'regulation_code': 'Public Law No. 123-456',
       'regulation_str': 'Public Law No.   123-456',
       'regulation_type': 'Public Law'}]),

    ("test Public Law 123-456 code",
     [('Public Law', 'Public Law No. 123-456')],
     [('Public Law', 'Public Law No. 123-456', 'Public Law 123-456')],
     [{'regulation_code': 'Public Law No. 123-456',
       'regulation_type': 'Public Law'}],
     [{'regulation_code': 'Public Law No. 123-456',
       'regulation_str': 'Public Law 123-456',
       'regulation_type': 'Public Law'}]),

    ("test Pub. Law 123-456 code",
     [('Public Law', 'Public Law No. 123-456')],
     [('Public Law', 'Public Law No. 123-456', 'Pub. Law 123-456')],
     [{'regulation_code': 'Public Law No. 123-456',
       'regulation_type': 'Public Law'}],
     [{'regulation_code': 'Public Law No. 123-456',
       'regulation_str': 'Pub. Law 123-456',
       'regulation_type': 'Public Law'}]),

    ("test Pub. L. 123-456 code",
     [('Public Law', 'Public Law No. 123-456')],
     [('Public Law', 'Public Law No. 123-456', 'Pub. L. 123-456')],
     [{'regulation_code': 'Public Law No. 123-456',
       'regulation_type': 'Public Law'}],
     [{'regulation_code': 'Public Law No. 123-456',
       'regulation_str': 'Pub. L. 123-456',
       'regulation_type': 'Public Law'}]),

    ("test 123 Stat. 456 code",
     [('Public Law', '123 Stat. 456')],
     [('Public Law', '123 Stat. 456', '123 Stat. 456')],
     [{'regulation_code': '123 Stat. 456', 'regulation_type': 'Public Law'}],
     [{'regulation_code': '123 Stat. 456',
       'regulation_str': '123 Stat. 456',
       'regulation_type': 'Public Law'}]),

    ("test Stat. 456 code", [], [], [], []),
    ("test AB USC 456 code", [], [], [], []),
    ("test 678 USC UPD code", [], [], [], []),
    ("test 678 USC UPD code", [], [], [], []),
    ("test 10 Public Law codes", [], [], [], []),
]


def test_get_regulations():
    """
    Test default get regulations behavior.
    :return:
    """
    for i, data in enumerate(TEST_DATA):
        text, res1, res2, res3, res4 = data
        print("Example {i}: {t}...".format(i=i, t=text[:40]))
        assert_list_equal(get_regulations(text, return_source=False, as_dict=False), res1)
        assert_list_equal(get_regulations(text, return_source=True, as_dict=False), res2)
        assert_list_equal(get_regulations(text, return_source=False, as_dict=True), res3)
        assert_list_equal(get_regulations(text, return_source=True, as_dict=True), res4)
