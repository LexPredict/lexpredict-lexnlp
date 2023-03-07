__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import os
from unittest import TestCase
import pandas as pd
from typing import List

from lexnlp.extract.common.base_path import lexnlp_test_path
from lexnlp.extract.common.annotations.law_annotation import LawAnnotation
# pylint:disable=no-name-in-module
from lexnlp.extract.de.laws import LawsParser, get_laws
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


def setup_parser():
    base_path = os.path.join(lexnlp_test_path, 'lexnlp/extract/de/laws/')
    gesetze_df = pd.read_csv(os.path.join(os.path.dirname(__file__),
                                          base_path + 'gesetze_list.csv'),
                             encoding="utf-8")

    verordnungen_df = pd.read_csv(os.path.join(os.path.dirname(__file__),
                                               base_path + 'verordnungen_list.csv'),
                                  encoding="utf-8")

    concept_df = pd.read_csv(os.path.join(os.path.dirname(__file__),
                                          base_path + 'de_concept_sample.csv'),
                             encoding="utf-8")

    law_parser = LawsParser(gesetze_df,
                            verordnungen_df,
                            concept_df)
    return law_parser


parser = setup_parser()


class TestParseDeLaws(TestCase):
    def test_parse_empty_text(self):
        ret = list(parser.parse(''))
        self.assertEqual(0, len(ret))
        ret = list(parser.parse("""

         """))
        self.assertEqual(0, len(ret))

    def test_parse_simply_phrase(self):
        text = "Dies ist durch das AAÜG geschehen."
        ret = list(parser.parse(text, 'x'))
        self.assertEqual(1, len(ret))
        self.assertEqual("x", ret[0].locale)
        self.assertEqual((18, 24), ret[0].coords)
        self.assertEqual('AAÜG', ret[0].name)
        self.assertEqual('AAÜG', ret[0].text)

        ret = list(parser.parse(text))
        self.assertEqual("de", ret[0].locale)

    # this test should be useful after implementing
    # courts loading from another dataframe
    def test_uninitialized(self):
        text = "Dies ist durch das AAÜG geschehen."
        # pylint: disable=unused-variable
        for _ in get_laws(text):
            pass

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_ordered_law_annotations,
            'lexnlp/typed_annotations/de/law/laws.txt',
            LawAnnotation)


def get_ordered_law_annotations(text: str) -> List[LawAnnotation]:
    ants = list(parser.parse(text))
    ants.sort(key=lambda a: a.coords[0])
    return ants
