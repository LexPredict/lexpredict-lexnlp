from unittest import TestCase

from lexnlp.extract.common.annotations.trademark_annotation import TrademarkAnnotation
from lexnlp.extract.en.trademarks import get_trademarks, get_trademark_annotations
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.7"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestTrademarksPlain(TestCase):

    def test_trademarks(self):
        text = "1.11.SCADA System means a supervisory control and data " + \
               "acquisition system such as the S/3 Software or Licensee's OASyS(R) product."
        ds = list(get_trademarks(text))
        self.assertEqual(1, len(ds))
        self.assertEqual('OASyS (R)', ds[0])

        ants = list(get_trademark_annotations(text))
        self.assertEqual(1, len(ants))
        self.assertEqual('en', ants[0].locale)
        self.assertEqual('OASyS (R)', ants[0].trademark)

        start = text.find('OASyS(R)')
        self.assertGreater(ants[0].coords[1], ants[0].coords[0])
        self.assertEqual((start, ants[0].coords[1]), ants[0].coords)

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_trademark_annotations,
            'lexnlp/typed_annotations/en/trademark/trademarks.txt',
            TrademarkAnnotation)
