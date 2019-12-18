import re
import time
import pandas

from unittest import TestCase
from lexnlp.extract.common.universal_court_parser import UniversalCourtsParser, ParserInitParams
from lexnlp.extract.en.courts import get_courts
from lexnlp.extract.en.dict_entities import entity_config
from lexnlp.extract.en.en_language_tokens import EnLanguageTokens
from lexnlp.tests.utility_for_testing import load_resource_document
from lexnlp.utils.lines_processing.line_processor import LineSplitParams

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestUniversalCourtsParser(TestCase):

    def test_check_match_attrs(self):
        parser = self.make_en_parser()
        text = load_resource_document(
            'lexnlp/extract/en/courts/courts_sample_01.txt', 'utf-8')
        ret_list = parser.parse(text)
        self.assertEqual(4, len(ret_list))

        for rv in [r.to_dictionary() for r in ret_list]:
            self.assertGreater(rv["attrs"]["end"], rv["attrs"]["start"])
            self.assertGreater(rv["attrs"]["end"], 0)
            self.assertGreater(len(rv["tags"]["Extracted Entity Type"]), 0)
            _ = text[rv["attrs"]["start"]:rv["attrs"]["end"]]
            # self.assertEqual(len(rf), len(rf.strip(' \t')))

    def test_compare_to_legacy_parser(self):
        parser = self.make_en_parser()
        text = load_resource_document(
            'lexnlp/extract/en/courts/courts_sample_01.txt', 'utf-8')

        start = time.time()
        ret_n = parser.parse(text)
        _ = (time.time() - start)
        self.assertEqual(4, len(ret_n))

        start = time.time()
        ret_l = [c for c in self.parse_courts_legacy_function(text)]
        __ = (time.time() - start)
        self.assertEqual(3, len(ret_l))

    def parse_courts_legacy_function(self, text: str):
        court_df = pandas \
            .read_csv(
            "https://raw.githubusercontent.com/LexPredict/lexpredict-legal-dictionary/1.0.2/en/legal/us_courts"
            ".csv")

        # Create config objects
        court_config_list = []
        for _, row in court_df.iterrows():
            c = entity_config(row["Court ID"], row["Court Name"], 0,
                              row["Alias"].split(";") if not pandas.isnull(row["Alias"]) else [])
            court_config_list.append(c)

        return get_courts(text, court_config_list)

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
