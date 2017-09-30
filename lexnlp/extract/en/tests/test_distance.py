#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Distance unit tests for English.

This module implements unit tests for the distance extraction functionality in English.

Todo:
    * More pathological and difficult cases
"""

# Imports

from nose.tools import assert_set_equal

from lexnlp.extract.en.distances import get_distances

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

EXAMPLE_DISTANCE = [
    "That is at least 10 miles away.",
    "That is at least 10mi away.",
    "That is at least 10 kilometers away.",
    "That is at least 10km away.",
    "That is somewhere between 5 miles and 10km from here.",
    "There are 10 dogs.",
    "That is a 20Hz oscillation.",
    "This is a 5khz test.",
    ", 500 miles to go",
    ",500.5 miles to go",
    ", fifty miles to the 5khz test.",
    " .5 miles to go",
    "There is no , distance here",
    "There are many miles to go",
    "There are ten miles to go",
    "There are 50 thousand miles to go",
    "There are fifty thousand miles to go",
    "This is not a 5.4.3.2.1 mi distance",
    "There are 5.4.3 thousand mi reasons"
]

RESULT = [
    [(10, "mile")],
    [(10, "mile")],
    [(10, "kilometer")],
    [(10, "kilometer")],
    [(5, "mile"), (10, "kilometer")],
    [],
    [],
    [],
    [(500, "mile")],
    [(500.5, "mile")],
    [(50, "mile")],
    [(0.5, "mile")],
    [],
    [],
    [(10, "mile")],
    [(50000, "mile")],
    [(50000, "mile")],
    [],
    [],
]

RESULT_SOURCE = [
    [(10.0, 'mile', '10 miles')],
    [(10.0, 'mile', '10mi')],
    [(10.0, 'kilometer', '10 kilometers')],
    [(10.0, 'kilometer', '10km')],
    [(5.0, 'mile', '5 miles'), (10.0, 'kilometer', '10km')],
    [],
    [],
    [],
    [(500.0, 'mile', '500 miles')],
    [(500.5, 'mile', '500.5 miles')],
    [(50, 'mile', 'fifty miles')],
    [(0.5, 'mile', '.5 miles')],
    [],
    [],
    [(10, 'mile', 'ten miles')],
    [(50000.0, 'mile', '50 thousand miles')],
    [(50000, 'mile', 'fifty thousand miles')],
    [],
    [],
]


def test_get_distance():
    """
    Test distance extraction.
    :return:
    """
    for i, example in enumerate(EXAMPLE_DISTANCE):
        print("Example {i}: {t}...".format(i=i, t=example[:40]))
        assert_set_equal(set(get_distances(example, return_sources=False)),
                         set(RESULT[i]))


def test_get_distance_source():
    """
    Test distance extraction with source.
    :return:
    """
    for i, example in enumerate(EXAMPLE_DISTANCE):
        print("Example {i}: {t}...".format(i=i, t=example[:40]))
        assert_set_equal(set(get_distances(example, return_sources=True)),
                         set(RESULT_SOURCE[i]))
