#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Duration unit tests for English.

This module implements unit tests for the duration extraction functionality in English.

Todo:
    * Better testing for exact test in return sources
    * More pathological and difficult cases

"""

# Imports

from lexnlp.extract.en.durations import get_durations
from lexnlp.tests import lexnlp_tests

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def test_get_durations():
    """
    Test durations.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(get_durations, return_sources=False,
                                                   expected_data_converter=lambda expected:
                                                   [(unit, float(duration_units), float(duration_days))
                                                    for unit, duration_units, duration_days in expected])


def test_get_durations_source():
    """
    Test durations with source.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(get_durations, return_sources=True,
                                                   expected_data_converter=lambda expected:
                                                   [(unit, float(duration_units), float(duration_days), source)
                                                    for unit, duration_units, duration_days, source in expected])
