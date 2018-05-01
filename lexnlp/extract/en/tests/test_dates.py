# !/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Date unit tests for English.

This module implements unit tests for the date extraction functionality in English.

Todo:
    * Implement document-level date detection to identify anomalous dates
    * Better testing for exact test in return sources
    * Resolve example bad dates
    * More pathological and difficult cases
"""

# Imports
import datetime
import random
import string

from nose.tools import assert_list_equal, assert_dict_equal, assert_equal

from lexnlp.extract.en.dates import get_dates_list, get_date_features, get_raw_date_list, train_default_model
from lexnlp.tests import lexnlp_tests

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

EXAMPLE_TEXT_1 = """Dear Jerry:
This amended and restated letter agreement sets forth the terms of your employment with Logitech Inc., a California 
corporation (the “Company”), as well as our understanding with respect to any termination of that employment 
relationship. Effective on the date set forth above, this letter agreement supersedes your offer letter dated January
28, 2008, in its entirety."""

# TODO: Improve classifier to handle
EXAMPLE_BAD_DATES = [
    ("""56 of March 22nd, 1983; Seismic Code by Executive Decree No.""",
     [datetime.date(1983, 3, 22)]),
]

DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def expected_data_converter(expected):
    ret = []
    for d in expected:
        if len(d) == 19:
            ret.append(datetime.datetime.strptime(d, DATETIME_FORMAT))
        else:
            if len(d) == 5:
                d = '{}-{}'.format(datetime.date.today().year, d)
            ret.append(datetime.datetime.strptime(d, DATE_FORMAT).date())
    return ret


def test_fixed_raw_dates():
    """
    Test raw date extraction from fixed examples.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(
        get_raw_date_list,
        expected_data_converter=expected_data_converter)


def test_fixed_dates():
    """
    Test date extraction from fixed examples.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(
        get_dates_list,
        expected_data_converter=expected_data_converter)


def test_fixed_dates_nonstrict():
    """
    Test date extraction from fixed examples.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(
        get_dates_list, strict=False,
        expected_data_converter=expected_data_converter)


def test_date_may():
    """
    Test that " may " alone does not parse.
    :return:
    """
    # Ensure that no value is returned for either strict or non-strict mode
    nonstrict_result = lexnlp_tests.benchmark_extraction_func(get_dates_list,
                                                              "this may be a date", strict=False, return_source=True)
    strict_result = get_dates_list("this may be a date", strict=True, return_source=True)
    assert_equal(len(nonstrict_result), 0)
    assert_equal(len(strict_result), 0)


def test_fixed_dates_source():
    """
    Test date extraction from fixed examples with source.
    :return:
    """
    lexnlp_tests.test_extraction_func_on_test_data(
        get_dates_list, return_source=True,
        expected_data_converter=expected_data_converter,
        actual_data_converter=lambda actual: [d[0] for d in actual])


def test_random_dates():
    """
    Test date extraction with random dates.
    :return:
    """
    # Check random examples
    n = 10

    # Iterate through all date range
    for _ in range(n):
        # Setup date
        year = random.randint(1980, 2020)
        month = random.randint(1, 13)
        day = random.randint(1, 32)

        try:
            date = datetime.date(year, month, day)
        except ValueError:
            continue

        # Try three versions
        text = """on {0}-{1}-{2}""".format(year, month, day)
        assert_list_equal(lexnlp_tests.benchmark_extraction_func(get_dates_list, text), [date])

        text = "by " + date.strftime("%b %d, %Y")
        assert_list_equal(lexnlp_tests.benchmark_extraction_func(get_dates_list, text), [date])

        text = "before " + date.strftime("%B %d, %Y")
        assert_list_equal(lexnlp_tests.benchmark_extraction_func(get_dates_list, text), [date])


def test_date_feature_1():
    """
    Test date feature engineering.
    :return:
    """
    date_feature = get_date_features("2000-02-02", 0, 10, include_bigrams=False, characters=string.printable)
    assert_dict_equal(date_feature,
                      {'char_T': 0.0, 'char_L': 0.0, 'char_?': 0.0, 'char_`': 0.0, 'char_B': 0.0, 'char_]': 0.0,
                       'char_Z': 0.0,
                       'char_&': 0.0, 'char_-': 0.2, 'char_/': 0.0, 'char_8': 0.0, 'char_c': 0.0, 'char_A': 0.0,
                       'char__': 0.0,
                       'char_I': 0.0, 'char_9': 0.0, 'char_V': 0.0, 'char_7': 0.0, 'char_b': 0.0, 'char_g': 0.0,
                       'char_!': 0.0,
                       'char_Q': 0.0, 'char_*': 0.0, 'char_{': 0.0, 'char_G': 0.0, 'char_.': 0.0, 'char_U': 0.0,
                       'char_\r': 0.0,
                       'char_:': 0.0, 'char_,': 0.0, 'char_\\': 0.0, 'char_$': 0.0, 'char_C': 0.0, 'char_\x0b': 0.0,
                       'char_S': 0.0,
                       'char_r': 0.0, 'char_J': 0.0, 'char_i': 0.0, 'char_1': 0.0, 'char_^': 0.0, 'char_l': 0.0,
                       'char_v': 0.0,
                       'char_m': 0.0, 'char_o': 0.0, 'char_h': 0.0, 'char_@': 0.0, 'char_\t': 0.0, 'char_M': 0.0,
                       'char_x': 0.0,
                       'char_2': 0.3, 'char_5': 0.0, 'char_"': 0.0, 'char_0': 0.5, 'char_q': 0.0, 'char_K': 0.0,
                       'char_R': 0.0,
                       'char_n': 0.0, 'char_4': 0.0, 'char_H': 0.0, 'char_p': 0.0, 'char_+': 0.0, 'char_O': 0.0,
                       'char_D': 0.0,
                       'char_)': 0.0, 'char_Y': 0.0, 'char_E': 0.0, 'char_<': 0.0, "char_'": 0.0, 'char_f': 0.0,
                       'char_t': 0.0,
                       'char_e': 0.0, 'char_W': 0.0, 'char_;': 0.0, 'char_s': 0.0, 'char_3': 0.0, 'char_}': 0.0,
                       'char_%': 0.0,
                       'char_P': 0.0, 'char_z': 0.0, 'char_N': 0.0, 'char_w': 0.0, 'char_\n': 0.0, 'char_d': 0.0,
                       'char_#': 0.0,
                       'char_u': 0.0, 'char_~': 0.0, 'char_>': 0.0, 'char_=': 0.0, 'char_k': 0.0, 'char_F': 0.0,
                       'char_ ': 0.0,
                       'char_\x0c': 0.0, 'char_|': 0.0, 'char_y': 0.0, 'char_(': 0.0, 'char_X': 0.0, 'char_[': 0.0,
                       'char_a': 0.0,
                       'char_j': 0.0, 'char_6': 0.0})


def test_date_feature_1_bigram():
    """
    Test date feature engineering with bigrams.
    :return:
    """
    date_feature = lexnlp_tests.benchmark_extraction_func(get_date_features,
                                                          "2000-02-02", start_index=0, end_index=10, include_bigrams=True, characters=string.digits)
    assert_dict_equal(date_feature,
                      {'bigram_02': 0.6666666666666666, 'bigram_06': 0.0, 'bigram_05': 0.0, 'bigram_58': 0.0,
                       'bigram_41': 0.0, 'bigram_13': 0.0, 'bigram_95': 0.0, 'bigram_37': 0.0, 'bigram_25': 0.0,
                       'bigram_92': 0.0, 'bigram_20': 0.3333333333333333, 'bigram_71': 0.0, 'bigram_29': 0.0,
                       'bigram_52': 0.0, 'bigram_67': 0.0, 'bigram_96': 0.0, 'bigram_64': 0.0, 'char_5': 0.0,
                       'bigram_27': 0.0, 'bigram_72': 0.0, 'bigram_80': 0.0, 'bigram_86': 0.0, 'bigram_12': 0.0,
                       'bigram_23': 0.0, 'bigram_38': 0.0, 'bigram_78': 0.0, 'bigram_14': 0.0, 'bigram_32': 0.0,
                       'bigram_45': 0.0, 'bigram_03': 0.0, 'bigram_83': 0.0, 'bigram_54': 0.0, 'char_1': 0.0,
                       'bigram_28': 0.0, 'bigram_69': 0.0, 'bigram_35': 0.0, 'bigram_85': 0.0, 'bigram_68': 0.0,
                       'bigram_51': 0.0, 'bigram_26': 0.0, 'bigram_47': 0.0, 'bigram_46': 0.0, 'char_2': 0.375,
                       'bigram_43': 0.0, 'bigram_48': 0.0, 'bigram_90': 0.0, 'char_0': 0.625, 'bigram_50': 0.0,
                       'bigram_56': 0.0, 'bigram_62': 0.0, 'char_4': 0.0, 'bigram_34': 0.0, 'bigram_70': 0.0,
                       'bigram_73': 0.0, 'bigram_15': 0.0, 'bigram_07': 0.0, 'bigram_30': 0.0, 'bigram_63': 0.0,
                       'bigram_74': 0.0, 'bigram_36': 0.0, 'bigram_19': 0.0, 'bigram_42': 0.0, 'bigram_53': 0.0,
                       'bigram_89': 0.0, 'bigram_40': 0.0, 'bigram_87': 0.0, 'bigram_01': 0.0, 'bigram_60': 0.0,
                       'bigram_76': 0.0, 'bigram_18': 0.0, 'bigram_09': 0.0, 'bigram_16': 0.0, 'bigram_24': 0.0,
                       'char_3': 0.0, 'bigram_10': 0.0, 'bigram_17': 0.0, 'bigram_65': 0.0, 'bigram_31': 0.0,
                       'bigram_93': 0.0, 'bigram_59': 0.0, 'bigram_91': 0.0, 'bigram_61': 0.0, 'bigram_82': 0.0,
                       'char_8': 0.0, 'char_9': 0.0, 'bigram_39': 0.0, 'bigram_49': 0.0, 'bigram_81': 0.0,
                       'bigram_97': 0.0, 'bigram_75': 0.0, 'bigram_84': 0.0, 'bigram_08': 0.0, 'bigram_98': 0.0,
                       'bigram_79': 0.0, 'bigram_21': 0.0, 'bigram_04': 0.0, 'char_7': 0.0, 'bigram_57': 0.0,
                       'char_6': 0.0, 'bigram_94': 0.0})


def test_build_model():
    """
    Test build model by running default train.
    :return:
    """
    train_default_model(save=False)
