#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Geo entity unit tests for English.

This module implements unit tests for the geo entity extraction functionality in English.

"""
import csv
import os

from lexnlp.extract.en.dict_entities import get_entity_name, entity_config, add_aliases_to_entity, \
    prepare_alias_blacklist_dict
from lexnlp.extract.en.geoentities import get_geoentities
from lexnlp.tests import lexnlp_tests

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def load_entities_dict():
    entities_fn = os.path.join(os.path.dirname(lexnlp_tests.this_test_data_path()), 'geoentities.csv')
    aliases_fn = os.path.join(os.path.dirname(lexnlp_tests.this_test_data_path()), 'geoaliases.csv')

    entities = {}

    with open(entities_fn, 'r', encoding='utf8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entities[row['id']] = entity_config(row['id'], row['name'], int(row['priority']) if row['priority'] else 0,
                                                name_is_alias=True)

    with open(aliases_fn, 'r', encoding='utf8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entity = entities.get(row['entity_id'])
            if entity:
                add_aliases_to_entity(entity,
                                      row['alias'],
                                      row['locale'],
                                      row['type'].startswith('iso') or row['type'] == 'abbreviation')
    return entities.values()


_CONFIG = list(load_entities_dict())


def test_geoentities():
    lexnlp_tests.test_extraction_func_on_test_data(get_geoentities, geo_config_list=_CONFIG,
                                                   actual_data_converter=lambda actual:
                                                   [get_entity_name(c[0]) for c in actual],
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
                                                   [(get_entity_name(c[0]), c[1][0]) for c in actual],
                                                   debug_print=True)


def test_geoentities_en_equal_match_take_top_prio():
    lexnlp_tests.test_extraction_func_on_test_data(get_geoentities, geo_config_list=_CONFIG,
                                                   priority=True,
                                                   text_languages='en',
                                                   actual_data_converter=lambda actual:
                                                   [(get_entity_name(c[0]), c[1][0]) for c in actual],
                                                   debug_print=True)


def test_geoentities_alias_filtering():
    prepared_alias_blacklist = prepare_alias_blacklist_dict([('Afghanistan', None, False), ('Mississippi', 'en', False),
                                                             ('AL', 'en', True)])
    lexnlp_tests.test_extraction_func_on_test_data(get_geoentities, geo_config_list=_CONFIG,
                                                   prepared_alias_black_list=prepared_alias_blacklist,
                                                   actual_data_converter=lambda actual:
                                                   [get_entity_name(c[0]) for c in actual],
                                                   debug_print=True,
                                                   start_from_csv_line=6)
