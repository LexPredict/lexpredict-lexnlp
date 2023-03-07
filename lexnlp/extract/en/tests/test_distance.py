#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Distance unit tests for English.

This module implements unit tests for the distance extraction functionality in English.

Todo:
    * More pathological and difficult cases
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# Imports
from decimal import Decimal
from lexnlp.extract.en.distances import get_distances
from lexnlp.tests import lexnlp_tests


def test_get_distance():
    """
    Test distance extraction.
    :return:
    """
    # TODO: Do we need this separate method? test_get_distance_source()
    #   ... tests both distances and sources
    lexnlp_tests.test_extraction_func_on_test_data(
        func=get_distances,
        return_sources=False,
        expected_data_converter=lambda expected: [
            (Decimal(distance), units)
            for distance, units in expected
        ]
    )


def test_get_distance_source():
    """
    Test distance extraction with source.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(
        func=get_distances,
        return_sources=True,
        expected_data_converter=lambda expected: [
            (Decimal(distance), units, source)
            for distance, units, source in expected
        ]
    )
