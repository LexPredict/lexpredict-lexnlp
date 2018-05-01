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
from lexnlp.tests import lexnlp_tests

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def test_get_regulations():
    """
    Test default get regulations behavior.
    :return:
    """

    lexnlp_tests.test_extraction_func_on_test_data(get_regulations,
                                                   expected_data_converter=lambda d:
                                                   [(reg_type, reg_code) for reg_type, reg_code, _reg_str in d],
                                                   return_source=False, as_dict=False)
    lexnlp_tests.test_extraction_func_on_test_data(get_regulations,
                                                   expected_data_converter=lambda d:
                                                   [(reg_type, reg_code, reg_str) for reg_type, reg_code, reg_str in d],
                                                   return_source=True, as_dict=False)

    # TODO Impl test_extraction_func_on_test_data() comparing lists of dicts
    for (_i, text, _input_args, expected) in lexnlp_tests.iter_test_data_text_and_tuple():
        expected_no_source_dict = [{'regulation_type': reg_type,
                                    'regulation_code': reg_code}
                                   for reg_type, reg_code, _reg_str in expected]
        expected_source_dict = [{'regulation_type': reg_type,
                                 'regulation_code': reg_code,
                                 'regulation_str': reg_str}
                                for reg_type, reg_code, reg_str in expected]
        assert_list_equal(
            list(lexnlp_tests.benchmark_extraction_func(get_regulations, text, return_source=False, as_dict=True)),
            expected_no_source_dict)
        assert_list_equal(
            list(lexnlp_tests.benchmark_extraction_func(get_regulations, text, return_source=True, as_dict=True)),
            expected_source_dict)
