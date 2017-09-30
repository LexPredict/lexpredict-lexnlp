#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Ratio unit tests for English.

This module implements unit tests for the ratio extraction functionality in English.

Todo:
    * Better testing for exact test in return sources
    * More pathological and difficult cases
"""

# Imports

from nose.tools import assert_set_equal
from lexnlp.extract.en.ratios import get_ratios

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

EXAMPLE_FIXED_RATIO = [("Ratio of not greater than 3.0:1.0.",
                        [(3.0, 1.0, 3.0)],
                        [(3.0, 1.0, 3.0, '3.0:1.0.')]),
                       ("Ratio of no more than four to one",
                        [(4.0, 1.0, 4.0)],
                        [(4, 1, 4.0, 'four to one')]),
                       ("Ratio of no more than four t one",
                        [], []),
                       ("Ratio of no more than four ot one",
                        [], []),
                       ("Ratio of no more than 4..0:1.0",
                        [], []),
                       ("Ratio of no more than 4.0:1..0",
                        [], []),
                       ("""Level I ----               1.0:1.0                  .18%
Level II       1.0:1.0                2.0:1.0                 .21%
Level III      2.0:1.0                -------                 .24%""",
                        [(1.0, 1.0, 1.0),
                         (1.0, 1.0, 1.0),
                         (2.0, 1.0, 2.0),
                         (2.0, 1.0, 2.0)],
                        [(1.0, 1.0, 1.0, '1.0:1.0'),
                         (1.0, 1.0, 1.0, '1.0:1.0'),
                         (2.0, 1.0, 2.0, '2.0:1.0'),
                         (2.0, 1.0, 2.0, '2.0:1.0')]),
                       ("""Ratio of 2.0::1.0""",
                        [], []),
                       ("""Don't catch time 8:30 a.m.""",
                        [], []),
                       ("""Don't catch time 8:30 am""",
                        [], []),
                       ("""Don't catch time 8:30 AM""",
                        [], []),
                       ("""Don't catch time 8:30 p.m.""",
                        [], []),
                       ("""Don't catch 0:30 pseudo ratio""",
                        [], []),
                       ("""Don't catch 30:0 pseudo ratio""",
                        [], []),
                       ]

EXAMPLE_FIXED_RATIO_NS = [("Ratio of not greater than 3.0:1.0.",
                           [(3.0, 1.0, 3.0)]),
                          ("Ratio of no more than four to one",
                           [(4.0, 1.0, 4.0)]),
                          ("Ratio of no more than four t one",
                           []),
                          ("Ratio of no more than four ot one",
                           []),
                          ("Ratio of no more than 4..0:1.0",
                           [(None, 1.0, None)]),
                          ("Ratio of no more than 4.0:1..0",
                           [(4.0, None, None)]),
                          ("""Level I ----               1.0:1.0                  .18%
Level II       1.0:1.0                2.0:1.0                 .21%
Level III      2.0:1.0                -------                 .24%""",
                           [(1.0, 1.0, 1.0),
                            (1.0, 1.0, 1.0),
                            (2.0, 1.0, 2.0),
                            (2.0, 1.0, 2.0)]),
                          ("""Ratio of 2.0::1.0""",
                           [(2.0, 1.0, 2.0)]),
                          ]


def test_get_ratios():
    """
    Test ratio extraction.
    :return:
    """
    for i, example in enumerate(EXAMPLE_FIXED_RATIO):
        print("Example {i}: {t}...".format(i=i, t=example[:40]))
        assert_set_equal(set(get_ratios(example[0], return_sources=False)),
                         set(example[1]))


def test_get_ratios_source():
    """
    Test ratio extraction with source.
    :return:
    """
    for i, example in enumerate(EXAMPLE_FIXED_RATIO):
        print("Example {i}: {t}...".format(i=i, t=example[:40]))
        assert_set_equal(set(get_ratios(example[0], return_sources=True)),
                         set(example[2]))
