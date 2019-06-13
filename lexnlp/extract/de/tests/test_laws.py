import os
from unittest import TestCase
import pandas as pd
from lexnlp.extract.de.laws import LawsParser, get_laws

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.6"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestParseDeLaws(TestCase):
    def test_parse_empty_text(self):
        parser = self.setup_parser()
        ret = parser.parse('')
        self.assertEqual(0, len(ret))
        ret = parser.parse("""

         """)
        self.assertEqual(0, len(ret))

    def test_parse_simply_phrase(self):
        parser = self.setup_parser()
        text = "Dies ist durch das AAÜG geschehen."
        ret = parser.parse(text, 'x')
        self.assertEqual(1, len(ret))
        self.assertEqual("x", ret[0].locale)

        ret = parser.parse(text)
        self.assertEqual("de", ret[0].locale)

    # this test should be useful after implementing
    # courts loading from another dataframe
    def test_uninitialized(self):
        text = "Dies ist durch das AAÜG geschehen."
        # pylint: disable=unused-variable
        for _ in get_laws(text):
            pass

    def setup_parser(self):
        base_path = os.path.dirname(__file__) + '/../../../../test_data/lexnlp/extract/de/laws/'
        gesetze_df = pd.read_csv(os.path.join(os.path.dirname(__file__),
                                 base_path + 'gesetze_list.csv'),
                                 encoding="utf-8")

        verordnungen_df = pd.read_csv(os.path.join(os.path.dirname(__file__),
                                      base_path + 'verordnungen_list.csv'),
                                      encoding="utf-8")

        concept_df = pd.read_csv(os.path.join(os.path.dirname(__file__),
                                 base_path + 'de_concept_sample.csv'),
                                 encoding="utf-8")

        parser = LawsParser(gesetze_df,
                            verordnungen_df,
                            concept_df)
        return parser
