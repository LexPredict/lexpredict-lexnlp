__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import re
import time
import pandas

from unittest import TestCase

from lexnlp.extract.en.dict_entities import DictionaryEntryAlias, DictionaryEntry
from lexnlp.extract.common.universal_court_parser import UniversalCourtsParser, ParserInitParams
from lexnlp.extract.en.courts import _get_courts
from lexnlp.extract.all_locales.courts import get_court_annotations as get_court_annotations_custom
from lexnlp.extract.en.en_language_tokens import EnLanguageTokens
from lexnlp.tests.utility_for_testing import load_resource_document
from lexnlp.utils.lines_processing.line_processor import LineSplitParams


class TestUniversalCourtsParser(TestCase):

    def test_check_match_attrs(self):
        parser = self.make_en_parser()
        text = load_resource_document('lexnlp/extract/en/courts/courts_sample_01.txt', 'utf-8')
        ret_list = list(parser.parse(text))
        self.assertEqual(4, len(ret_list))

        for rv in [r.to_dictionary() for r in ret_list]:
            self.assertGreater(rv["attrs"]["end"], rv["attrs"]["start"])
            self.assertGreater(rv["attrs"]["end"], 0)
            self.assertGreater(len(rv["tags"]["Extracted Entity Type"]), 0)
            _ = text[rv["attrs"]["start"]:rv["attrs"]["end"]]
            # self.assertEqual(len(rf), len(rf.strip(' \t')))

    def test_compare_to_legacy_parser(self):
        parser = self.make_en_parser()
        text = load_resource_document('lexnlp/extract/en/courts/courts_sample_01.txt', 'utf-8')

        start = time.time()
        ret_n = list(parser.parse(text))
        _ = (time.time() - start)
        self.assertEqual(4, len(ret_n))

        start = time.time()
        ret_l = list(self.parse_courts_legacy_function(text))
        __ = (time.time() - start)
        self.assertEqual(3, len(ret_l))

    def test_legacy_parse_court_annotations(self):
        court_config_list = self.load_en_courts()
        text = load_resource_document(
            'lexnlp/extract/en/courts/courts_sample_01.txt', 'utf-8')
        ants = list(get_court_annotations_custom(
            'en', text, court_config_list))
        self.assertEqual(3, len(ants))
        self.assertEqual('court', ants[0].record_type)

    def parse_courts_legacy_function(self, text: str):
        court_config_list = self.load_en_courts()
        return _get_courts(text, court_config_list)

    def load_en_courts(self):
        court_df = pandas.read_csv(
            "https://raw.githubusercontent.com/LexPredict/lexpredict-legal-dictionary/1.0.2/en/legal/us_courts.csv"
        )
        # Create config objects
        court_config_list = []
        for _, row in court_df.iterrows():
            aliases = []
            if not pandas.isnull(row['Alias']):
                aliases = [DictionaryEntryAlias(r) for r in row['Alias'].split(';')]
            c = DictionaryEntry(id=int(row['Court ID']),
                                name=row['Court Name'],
                                priority=0,
                                name_is_alias=True,
                                aliases=aliases)
            court_config_list.append(c)
        return court_config_list

    def make_en_parser(self):
        url = "https://raw.githubusercontent.com/LexPredict/lexpredict-legal-dictionary/1.0.2/en/legal/us_courts.csv"

        ptrs = ParserInitParams()
        ptrs.court_pattern_checker = re.compile('court', re.IGNORECASE)
        ptrs.dataframe_paths = [url]
        ptrs.split_ptrs = LineSplitParams()
        ptrs.split_ptrs.line_breaks = {'\n', '.', ';', ','}.union(set(EnLanguageTokens.conjunctions))
        ptrs.split_ptrs.abbreviations = EnLanguageTokens.abbreviations
        ptrs.split_ptrs.abbr_ignore_case = True

        parser = UniversalCourtsParser(ptrs)
        return parser
