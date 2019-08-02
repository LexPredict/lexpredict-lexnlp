from unittest import TestCase

from lexnlp.extract.common.annotations.percent_annotation import PercentAnnotation
from lexnlp.extract.en.percents import get_percents, get_percent_annotations
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.7"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestPercentPlain(TestCase):

    def test_percent(self):
        text = "I'm 146.5 percent sure (or just 100%)"
        ds = list(get_percents(text))
        self.assertEqual(2, len(ds))

        ants = list(get_percent_annotations(text))
        self.assertEqual(2, len(ds))
        self.assertEqual('en', ants[0].locale)
        self.assertEqual('percent', ants[0].sign)
        self.assertEqual(146.5, ants[0].amount)

        self.assertEqual('%', ants[1].sign)
        self.assertEqual(100.0, ants[1].amount)

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_percent_annotations,
            'lexnlp/typed_annotations/en/percent/percents.txt',
            PercentAnnotation)
