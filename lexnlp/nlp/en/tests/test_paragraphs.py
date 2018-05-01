#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Imports
import string

# Test imports
from nose.tools import assert_dict_equal, nottest, assert_equal, assert_in

# Project imports
from lexnlp.nlp.en.segments.paragraphs import get_paragraphs
from lexnlp.nlp.en.segments.utils import build_document_distribution
from lexnlp.tests import lexnlp_tests

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

DOCUMENT_EXAMPLE_1 = "this is a test 123!"
DOCUMENT_EXAMPLE_1_RESULT_LC = {'doc_char_s': 0.2727272727272727, 'doc_char_p': 0.0, 'doc_char_a': 0.09090909090909091,
                                'doc_char_f': 0.0, 'doc_char_q': 0.0, 'doc_char_j': 0.0, 'doc_char_z': 0.0,
                                'doc_char_n': 0.0, 'doc_char_r': 0.0, 'doc_char_m': 0.0, 'doc_char_y': 0.0,
                                'doc_char_t': 0.2727272727272727, 'doc_char_b': 0.0, 'doc_char_w': 0.0,
                                'doc_char_v': 0.0, 'doc_char_c': 0.0, 'doc_char_h': 0.09090909090909091,
                                'doc_char_i': 0.18181818181818182, 'doc_char_e': 0.09090909090909091, 'doc_char_k': 0.0,
                                'doc_char_x': 0.0, 'doc_char_g': 0.0, 'doc_char_l': 0.0, 'doc_char_d': 0.0,
                                'doc_char_o': 0.0, 'doc_char_u': 0.0}
DOCUMENT_EXAMPLE_1_RESULT_DI = {'doc_char_1': 0.3333333333333333, 'doc_char_3': 0.3333333333333333,
                                'doc_char_2': 0.3333333333333333, 'doc_char_6': 0.0, 'doc_char_0': 0.0,
                                'doc_char_7': 0.0, 'doc_char_9': 0.0, 'doc_char_5': 0.0, 'doc_char_4': 0.0,
                                'doc_char_8': 0.0}
DOCUMENT_EXAMPLE_1_RESULT_CUSTOM = {'doc_char_1': 0.3333333333333333, 'doc_char_3': 0.3333333333333333,
                                    'doc_char_2': 0.3333333333333333}
DOCUMENT_EXAMPLE_1_RESULT_CUSTOM_NO_NORM = {'doc_char_1': 1, 'doc_char_3': 1, 'doc_char_2': 1}
DOCUMENT_EXAMPLE_1_RESULT_PRINT = {'doc_char_1': 0.05263157894736842, 'doc_char_Q': 0.0, 'doc_char_y': 0.0,
                                   'doc_char_W': 0.0, 'doc_char_6': 0.0, 'doc_char_j': 0.0, 'doc_char_|': 0.0,
                                   'doc_char_n': 0.0, 'doc_char_?': 0.0, 'doc_char_4': 0.0, 'doc_char__': 0.0,
                                   'doc_char_m': 0.0, 'doc_char_Y': 0.0, 'doc_char_E': 0.0, 'doc_char_[': 0.0,
                                   'doc_char_b': 0.0, 'doc_char_O': 0.0, 'doc_char_K': 0.0, 'doc_char_`': 0.0,
                                   'doc_char_h': 0.05263157894736842, 'doc_char_"': 0.0, 'doc_char_U': 0.0,
                                   'doc_char_B': 0.0, 'doc_char_V': 0.0, 'doc_char_%': 0.0, 'doc_char_8': 0.0,
                                   'doc_char_!': 0.05263157894736842, 'doc_char_<': 0.0, 'doc_char_(': 0.0,
                                   'doc_char_,': 0.0, 'doc_char_w': 0.0, 'doc_char_*': 0.0, 'doc_char_g': 0.0,
                                   'doc_char_H': 0.0, 'doc_char_I': 0.0, 'doc_char_/': 0.0,
                                   'doc_char_ ': 0.21052631578947367, 'doc_char_\x0c': 0.0, 'doc_char_L': 0.0,
                                   'doc_char_-': 0.0, 'doc_char_\\': 0.0, 'doc_char_9': 0.0, 'doc_char_5': 0.0,
                                   'doc_char_N': 0.0, 'doc_char_>': 0.0, 'doc_char_7': 0.0, 'doc_char_$': 0.0,
                                   'doc_char_\r': 0.0, 'doc_char_i': 0.10526315789473684, 'doc_char_\n': 0.0,
                                   'doc_char_.': 0.0, 'doc_char_k': 0.0, 'doc_char_C': 0.0, 'doc_char_R': 0.0,
                                   'doc_char_u': 0.0, 'doc_char_p': 0.0, 'doc_char_f': 0.0, 'doc_char_q': 0.0,
                                   'doc_char_3': 0.05263157894736842, 'doc_char_z': 0.0, 'doc_char_F': 0.0,
                                   'doc_char_r': 0.0, 'doc_char_M': 0.0, 'doc_char_;': 0.0,
                                   'doc_char_a': 0.05263157894736842, 'doc_char_D': 0.0,
                                   'doc_char_t': 0.15789473684210525, "doc_char_'": 0.0, 'doc_char_x': 0.0,
                                   'doc_char_X': 0.0, 'doc_char_~': 0.0, 'doc_char_:': 0.0, 'doc_char_&': 0.0,
                                   'doc_char_{': 0.0, 'doc_char_o': 0.0, 'doc_char_l': 0.0, 'doc_char_d': 0.0,
                                   'doc_char_^': 0.0, 'doc_char_s': 0.15789473684210525, 'doc_char_S': 0.0,
                                   'doc_char_}': 0.0, 'doc_char_v': 0.0, 'doc_char_+': 0.0, 'doc_char_P': 0.0,
                                   'doc_char_T': 0.0, 'doc_char_\t': 0.0, 'doc_char_0': 0.0, 'doc_char_G': 0.0,
                                   'doc_char_#': 0.0, 'doc_char_=': 0.0, 'doc_char_\x0b': 0.0, 'doc_char_]': 0.0,
                                   'doc_char_c': 0.0, 'doc_char_A': 0.0, 'doc_char_e': 0.05263157894736842,
                                   'doc_char_2': 0.05263157894736842, 'doc_char_J': 0.0, 'doc_char_)': 0.0,
                                   'doc_char_@': 0.0, 'doc_char_Z': 0.0}


def test_document_distribution_1_lc():
    """
    Test lowercase letters only.
    :return:
    """
    # Check all dictionaries
    assert_dict_equal(DOCUMENT_EXAMPLE_1_RESULT_LC,
                      lexnlp_tests.benchmark_extraction_func(build_document_distribution,
                                                             DOCUMENT_EXAMPLE_1, characters=string.ascii_lowercase))


def test_document_distribution_1_digits():
    """
    Test digits only.
    :return:
    """
    # Check all dictionaries
    assert_dict_equal(DOCUMENT_EXAMPLE_1_RESULT_DI,
                      lexnlp_tests.benchmark_extraction_func(build_document_distribution,
                                                             DOCUMENT_EXAMPLE_1, characters=string.digits))


def test_document_distribution_1_custom():
    """
    Test custom set.
    :return:
    """
    # Check all dictionaries
    assert_dict_equal(DOCUMENT_EXAMPLE_1_RESULT_CUSTOM,
                      lexnlp_tests.benchmark_extraction_func(build_document_distribution,
                                                             DOCUMENT_EXAMPLE_1, characters=['1', '2', '3']))


def test_document_distribution_1_custom_nn():
    """
    Test custom set.
    :return:
    """
    # Check all dictionaries
    assert_dict_equal(DOCUMENT_EXAMPLE_1_RESULT_CUSTOM_NO_NORM,
                      lexnlp_tests.benchmark_extraction_func(build_document_distribution,
                                                             DOCUMENT_EXAMPLE_1,
                                                             characters=['1', '2', '3'], norm=False))


def test_document_distribution_1_print():
    """
    Test all printable.
    :return:
    """
    # Check all dictionaries
    assert_dict_equal(DOCUMENT_EXAMPLE_1_RESULT_PRINT,
                      lexnlp_tests.benchmark_extraction_func(build_document_distribution,
                                                             DOCUMENT_EXAMPLE_1, characters=string.printable))


def test_document_distribution_empty():
    """
    Test all printable.
    :return:
    """
    # Check all dictionaries
    _ = lexnlp_tests.benchmark_extraction_func(build_document_distribution,
                                               "", characters=string.printable)


@nottest
def run_paragraph_test(text, result, window_pre=3, window_post=3):
    """
    Base test method to run against text with given results.
    """

    def remove_whitespace(r):
        return r.replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")

    # Get list from text
    para_list = list(lexnlp_tests.benchmark_extraction_func(get_paragraphs, text,
                                                            window_pre=window_pre, window_post=window_post))

    # Check length first
    assert_equal(len(para_list), len(result))

    # Check each sentence matches
    clean_result = [remove_whitespace(para) for para in result]
    for para in para_list:
        assert_in(remove_whitespace(para), clean_result)


def test_paragraph_examples():
    for (_i, text, _input_args, expected) in lexnlp_tests.iter_test_data_text_and_tuple():
        run_paragraph_test(text, expected)
