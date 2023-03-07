# -*- coding: utf-8 -*-

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import csv
import os
from typing import List
from unittest import TestCase

from lexnlp.extract.common.annotations.court_annotation import CourtAnnotation
from lexnlp.extract.en.courts import get_courts, get_court_annotations, get_court_list, _get_courts
from lexnlp.extract.en.dict_entities import DictionaryEntryAlias, DictionaryEntry
from lexnlp.tests.lexnlp_tests import DIR_ROOT
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


class TestCourtsPlain(TestCase):
    def test_bankr_courts(self):
        text = 'One one Bankr. E.D.N.C. two two two.'
        courts = list(_get_courts(text, court_config_list=self.build_courts_config()))
        self.assertEqual(1, len(courts))

    def test_bankr_courts_wo_nltk(self):
        text = 'One one Bankr. E.D.N.C. two two two.'
        courts = list(_get_courts(text, court_config_list=self.build_courts_config(), simplified_normalization=True))
        self.assertEqual(1, len(courts))

    def test_bankr_court_annotations(self):
        text = 'One one Bankr. E.D.N.C. two two two.'
        courts = list(get_court_annotations(text))
        self.assertEqual(2, len(courts))

    def build_courts_config(self) -> List[DictionaryEntry]:
        courts_config_fn = os.path.join(DIR_ROOT, 'test_data/lexnlp/extract/en/tests/test_courts/us_courts.csv')
        courts_config_list = []
        with open(courts_config_fn, 'r', encoding='utf8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                aliases = []
                if row['Alias']:
                    aliases = [DictionaryEntryAlias(r) for r in row['Alias'].split(';')]
                cc = DictionaryEntry(id=int(row['Court ID']),
                                     name=row['Court Type'] + '|' + row['Court Name'],
                                     priority=0,
                                     name_is_alias=False,
                                     aliases=aliases,
                                     )
                cc.aliases.append(DictionaryEntryAlias(row['Court Name']))
                courts_config_list.append(cc)
        return courts_config_list

    def test_parse_empty_text(self):
        ret = get_court_list('')
        self.assertEqual(0, len(ret))
        get_court_list("""
         """)
        #self.assertEqual(0, len(ret))

    def test_parse_simply_text(self):
        text = "A recent decision by a United States Supreme Court in Alabama v. Ballyshear LLC confirms that a key factor is the location of the impact of the alleged discriminatory conduct."
        ret = get_court_list(text)
        self.assertEqual(1, len(ret))
        self.assertEqual("en", ret[0].locale)

        ret = get_court_list(text, "z")
        self.assertEqual("z", ret[0].locale)

        items = list(get_courts(text))
        court_name = items[0]["tags"]["Extracted Entity Court Name"]
        self.assertEqual('United States Supreme Court', court_name)

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_court_annotations,
            'lexnlp/typed_annotations/en/court/courts.txt',
            CourtAnnotation)
