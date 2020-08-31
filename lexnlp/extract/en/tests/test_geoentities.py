#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Geo entity unit tests for English.

This module implements unit tests for the geo entity extraction functionality in English.

"""

import os

from lexnlp.extract.common.base_path import lexnlp_test_path
from lexnlp.extract.en.dict_entities import prepare_alias_banlist_dict, AliasBanRecord
from lexnlp.extract.en.geoentities import get_geoentities, load_entities_dict_by_path
from lexnlp.tests import lexnlp_tests

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def load_entities_dict():
    base_path = os.path.join(lexnlp_test_path, 'lexnlp/extract/en/tests/test_geoentities')
    entities_fn = os.path.join(base_path, 'geoentities.csv')
    aliases_fn = os.path.join(base_path, 'geoaliases.csv')
    return load_entities_dict_by_path(entities_fn, aliases_fn)


_CONFIG = list(load_entities_dict())


def test_geoentities():
    lexnlp_tests.test_extraction_func_on_test_data(get_geoentities, geo_config_list=_CONFIG,
                                                   actual_data_converter=lambda actual:
                                                   [c[0].name for c in actual],
                                                   debug_print=True)


def test_geoentities_counting():
    text = 'And AND AND AND And'
    actual = list(get_geoentities(text, geo_config_list=_CONFIG))
    assert len(actual) == 3


def test_geoentities_en_equal_match_take_lowest_id():
    lexnlp_tests.test_extraction_func_on_test_data(get_geoentities, geo_config_list=_CONFIG,
                                                   priority_by_id=True,
                                                   text_languages='en',
                                                   actual_data_converter=lambda actual:
                                                   [(c[0].name, c[1].alias) for c in actual],
                                                   debug_print=True)


def test_geoentities_en_equal_match_take_top_prio():
    lexnlp_tests.test_extraction_func_on_test_data(get_geoentities, geo_config_list=_CONFIG,
                                                   priority=True,
                                                   text_languages='en',
                                                   actual_data_converter=lambda actual:
                                                   [(c[0].name, c[1].alias) for c in actual],
                                                   debug_print=True)


def test_geoentities_alias_filtering():
    prepared_alias_banlist = prepare_alias_banlist_dict(
        [AliasBanRecord('Afghanistan', None, False),
         AliasBanRecord('Mississippi', 'en', False),
         AliasBanRecord('AL', 'en', True)])
    lexnlp_tests.test_extraction_func_on_test_data(get_geoentities, geo_config_list=_CONFIG,
                                                   prepared_alias_ban_list=prepared_alias_banlist,
                                                   actual_data_converter=lambda actual:
                                                   [c[0].name for c in actual],
                                                   debug_print=True,
                                                   start_from_csv_line=6)
