#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Distance unit tests for English.

This module implements unit tests for the distance extraction functionality in English.

Todo:
    * More pathological and difficult cases
"""

# Imports

from lexnlp.extract.en.distances import get_distances
from lexnlp.tests import lexnlp_tests

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def test_get_distance():
    """
    Test distance extraction.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(get_distances, return_sources=False,
                                                   expected_data_converter=lambda expected:
                                                   [(float(distance), units) for distance, units in expected])
    # TODO: Do we need this separate method? test_get_distance_source() tests both distances and sources


def test_get_distance_source():
    """
    Test distance extraction with source.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(get_distances, return_sources=True,
                                                   expected_data_converter=lambda expected:
                                                   [(float(distance), units, source) for distance, units, source in
                                                    expected])
