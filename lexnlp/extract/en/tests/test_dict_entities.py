#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Dict entity general unit tests.

"""

from unittest import TestCase

from nose.tools import assert_dict_equal, assert_true, assert_false, assert_equals

from lexnlp.extract.en.dict_entities import find_dict_entities, entity_config, entity_alias, get_entity_name, \
    normalize_text, prepare_alias_blacklist_dict, alias_is_blacklisted, get_entity_id, get_alias_id, get_alias_text
from lexnlp.tests import lexnlp_tests

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestDictEntities(TestCase):
    def test_common_search_all_languages(self):
        some_entity = entity_config(1, 'Some Entity', aliases=['Something'])
        text = 'Some Entity should be found in this text.'

        expected = ((some_entity[1], 'Some Entity'),)

        lexnlp_tests.test_extraction_func(expected,
                                          find_dict_entities,
                                          text,
                                          all_possible_entities=[some_entity],
                                          actual_data_converter=lambda actual:
                                          [(get_entity_name(c.entity[0]), c.entity[1][0]) for c in actual],
                                          debug_print=True)

    def test_conflicts_take_longest_match(self):
        some_entity = entity_config(1, 'Some Entity', aliases=['Something'])
        some_entity1 = entity_config(2, 'Some Entity One', aliases=['Something One'])
        some_entity2 = entity_config(3, 'Some Entity Two', aliases=['Something Two'])
        entities = [some_entity, some_entity1, some_entity2]

        text = '"Some Entity One" should be found in this text and "Someee Entityyy" should be ignored.'

        expected = ((some_entity1[1], 'Some Entity One'),)

        lexnlp_tests.test_extraction_func(expected, find_dict_entities, text,
                                          all_possible_entities=entities,
                                          actual_data_converter=lambda actual:
                                          [(get_entity_name(c.entity[0]), c.entity[1][0]) for c in actual],
                                          debug_print=True)

    def test_conflicts_equal_length_take_same_language(self):
        some_entity = entity_config(1, 'Some Entity', aliases=['Something'])
        some_entity1 = entity_config(2, 'Some Entity1', aliases=[entity_alias('Some Entity One', language='fr')])
        some_entity2 = entity_config(3, 'Some Entity2', aliases=['Something Two'])
        entities = [some_entity, some_entity1, some_entity2]

        text = '"Some Entity One" should not be found in this text because it is not in German language.' \
               'Shorter match - "Someeee Entityyy" should be taken instead.'

        expected = ((some_entity[1], 'Some Entity'),)

        lexnlp_tests.test_extraction_func(expected, find_dict_entities, text,
                                          all_possible_entities=entities,
                                          text_languages=['de'],
                                          actual_data_converter=lambda actual:
                                          [(get_entity_name(c.entity[0]), c.entity[1][0]) for c in actual],
                                          debug_print=True)

    def test_equal_aliases_in_dif_languages(self):
        mississippi = entity_config(1, 'Mississippi', aliases=[entity_alias('MS', is_abbreviation=True, language='en'),
                                                               entity_alias('Mississippi', language='de'),
                                                               entity_alias('Mississippi', language='en')])
        montserrat = entity_config(2, 'Montserrat', aliases=[entity_alias('MS', is_abbreviation=True, language='en'),
                                                             entity_alias('Montserrat', language='de'),
                                                             entity_alias('Montserrat', language='en')])
        canada = entity_config(3, 'Canada', aliases=[entity_alias('CAN', is_abbreviation=True, language='en'),
                                                     entity_alias('Kanada', language='de'),
                                                     entity_alias('Canada', language='en')])
        entities = [mississippi, montserrat, canada]

        text = '"MS" here can mean either "MMMississippi" or "MMMontserrat" because they have equal aliases in English. ' \
               'This test is here because in one version of the code alias texts were required to be unique. ' \
               '"CCCanada" (can) should not be detected because word "can" is in lowercase here.'

        expected = ((mississippi[1], 'MS'), (montserrat[1], 'MS'))

        lexnlp_tests.test_extraction_func(expected, find_dict_entities, text,
                                          all_possible_entities=entities,
                                          text_languages=['en'],
                                          actual_data_converter=lambda actual:
                                          [(get_entity_name(c.entity[0]), c.entity[1][0]) for c in actual],
                                          debug_print=True)

    def test_abbreviations_simple(self):
        some_entity = entity_config(1, 'ITAbbrev', aliases=[entity_alias('IT', is_abbreviation=True)])
        some_entity1 = entity_config(2, 'ISAbbrev', aliases=[entity_alias('IS', is_abbreviation=True)])
        entities = [some_entity, some_entity1]

        text = '"IT\'s" entity should be detected even with "\'s" because tokenizer takes care of this kind of things. ' \
               '"ISS" entity should not be detected - bacause "is" word' \
               ' is in lowercase here and probably does not mean an abbreviation.'

        expected = ((some_entity[1], 'IT'),)

        lexnlp_tests.test_extraction_func(expected, find_dict_entities, text,
                                          all_possible_entities=entities,
                                          text_languages=['ge'],
                                          actual_data_converter=lambda actual:
                                          [(get_entity_name(c.entity[0]), c.entity[1][0]) for c in actual],
                                          debug_print=True)

    def test_plural_case_matching(self):
        table = entity_config(1, 'Table', aliases=[entity_alias('tbl.', is_abbreviation=True)], name_is_alias=True)

        man = entity_config(2, 'man', name_is_alias=True)

        masloboyka = entity_config(3, 'masloboyka', name_is_alias=True)

        entities = [table, man, masloboyka]

        text = 'We should detect the singular number of word "tables" here - the stemmer takes care of plural case. ' \
               'Unfortunately our stemmer is not able to convert word "men" to singular number yet :(. ' \
               'But it works for word "masloboykas" - a non existing word in English in plural case.'

        expected = ((masloboyka[1], 'masloboyka'),)

        lexnlp_tests.test_extraction_func(expected, find_dict_entities, text,
                                          all_possible_entities=entities,
                                          use_stemmer=True,
                                          actual_data_converter=lambda actual:
                                          [(get_entity_name(c.entity[0]), c.entity[1][0]) for c in actual],
                                          debug_print=True)

    def test_normalize_text(self):
        lexnlp_tests.test_extraction_func_on_test_data(normalize_text,
                                                       actual_data_converter=lambda text: (text,), debug_print=True)

    def test_prepare_alias_blacklist_dict(self):
        src = [('Alias1', 'lang1', False), ('ABBREV1', 'lang1', True), ('Alias2', None, False),
               ('Alias3', 'lang1', False)]
        actual = prepare_alias_blacklist_dict(src, use_stemmer=False)
        expected = {
            'lang1': ([' alias1 ', ' alias3 '], [' ABBREV1 ']),
            None: ([' alias2 '], [])
        }
        assert_dict_equal(actual, expected)

        assert_true(prepare_alias_blacklist_dict([]) is None)

    def test_alias_is_blacklisted(self):
        src = [('Alias1', 'lang1', False), ('ABBREV1', 'lang1', True), ('Alias2', None, False),
               ('Alias3', 'lang1', False)]
        prepared = prepare_alias_blacklist_dict(src, use_stemmer=False)
        assert_true(alias_is_blacklisted(prepared, ' ABBREV1 ', 'lang1', True))
        assert_false(alias_is_blacklisted(prepared, ' AAA ', 'lang1', True))
        assert_false(alias_is_blacklisted(None, 'aaaa', 'l', False))

    def test_get_entity_id(self):
        entity = (1, 'name', [])
        assert_equals(1, get_entity_id(entity))

    def test_find_dict_entities_empty_text(self):
        text = ''
        am = entity_config(1, 'America', aliases=[entity_alias('AM', is_abbreviation=True)], name_is_alias=False)

        res = list(find_dict_entities(text, [am]))
        assert_false(res)

    def test_get_alias_id(self):
        alias = entity_alias('alias', 'lang', False, 123)
        assert_equals(123, get_alias_id(alias))

    def test_get_alias_text(self):
        alias = entity_alias('alias', 'lang', False, 123)
        assert_equals('alias', get_alias_text(alias))

    def test_am_pm_none(self):
        am = entity_config(1, 'America', aliases=[entity_alias('AM', is_abbreviation=True)], name_is_alias=False)
        pm = entity_config(2, 'Postmodernism', aliases=[entity_alias('PM', is_abbreviation=True)], name_is_alias=False)

        entities = [am, pm]
        ents = list(find_dict_entities('It is 11:00 AM or 11:00 PM now.',
            all_possible_entities=entities))
        self.assertEqual(0, len(ents))

        ents = list(find_dict_entities('It is 11:00am now in (AM). Hello!',
                                       all_possible_entities=entities))
        self.assertEqual(1, len(ents))
        self.assertEqual('America', ents[0].entity[0][1])

        ents = list(find_dict_entities('It is 11:00am now.',
                                       all_possible_entities=entities))
        self.assertEqual(0, len(ents))
