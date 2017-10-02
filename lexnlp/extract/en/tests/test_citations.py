#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Citation unit tests for English.

This module implements unit tests for the citation extraction functionality in English.

Todo:
    * Better testing for exact test in return sources
    * More pathological and difficult cases
"""

# Imports

from nose.tools import assert_list_equal
from lexnlp.extract.en.citations import get_citations

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

TEST_DATA = [
    ("bob lissner v. test 1 F.2d 1, 2-5 (2d Cir., 1982)",
     [(1, 'F.2d', 'Federal Reporter', 1, '2-5', '2d Cir.', 1982)],
     [(1, 'F.2d', 'Federal Reporter', 1, '2-5', '2d Cir.', 1982, '1 F.2d 1, 2-5 (2d Cir., 1982)')]),
    ("bob lissner v. test 1 F.2d 1, 2-5 (1982)",
     [(1, 'F.2d', 'Federal Reporter', 1, '2-5', None, 1982)],
     [(1, 'F.2d', 'Federal Reporter', 1, '2-5', None, 1982, '1 F.2d 1, 2-5 (1982)')]),
    ("bob lissner v. test 1 F.2d 1, 25 (1982)",
     [(1, 'F.2d', 'Federal Reporter', 1, '25', None, 1982)],
     [(1, 'F.2d', 'Federal Reporter', 1, '25', None, 1982, '1 F.2d 1, 25 (1982)')]),
    ("bob lissner v. test 1 F.2d 1 (1982)",
     [(1, 'F.2d', 'Federal Reporter', 1, None, None, 1982)],
     [(1, 'F.2d', 'Federal Reporter', 1, None, None, 1982, '1 F.2d 1 (1982)')]),
    ("bob lissner v. test 1 F.2d 1",
     [(1, 'F.2d', 'Federal Reporter', 1, None, None, None)],
     [(1, 'F.2d', 'Federal Reporter', 1, None, None, None, '1 F.2d 1')]),
    ("bob lissner v. test 1 F.2d",
     [],
     []),
    ("bob lissner v. test 1 F.2d 1, 2-5 (25 Fed. Cl. 20)",
     [(1, 'F.2d', 'Federal Reporter', 1, '2-5', None, None),
      (25, 'Fed. Cl.', 'United States Claims Court Reporter', 20, None, None, None)],
     [(1, 'F.2d', 'Federal Reporter', 1, '2-5', None, None, '1 F.2d 1, 2-5'),
      (25, 'Fed. Cl.', 'United States Claims Court Reporter', 20, None, None, None, '25 Fed. Cl. 20')
      ]),
    (" 8050 S.W. 10th Street",
     [],
     []),
]


def test_get_citations():
    """
    Test default get citation behavior.
    :return:
    """
    for i, data in enumerate(TEST_DATA):
        text, res1, res2 = data
        print("Example {i}: {t}...".format(i=i, t=text[:40]))
        assert_list_equal(get_citations(text, return_source=False), res1)
        assert_list_equal(get_citations(text, return_source=True), res2)


def test_get_citations_as_dict():
    assert_list_equal(
        get_citations(TEST_DATA[0][0],
                      return_source=True,
                      as_dict=True),
        [{'citation_str': '1 F.2d 1, 2-5 (2d Cir., 1982)',
          'court': '2d Cir.',
          'page': 1,
          'page2': '2-5',
          'reporter': 'F.2d',
          'reporter_full_name': 'Federal Reporter',
          'volume': 1,
          'year': 1982}]
    )
