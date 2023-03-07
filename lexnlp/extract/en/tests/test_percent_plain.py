__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from unittest import TestCase
from decimal import Decimal
from lexnlp.extract.common.annotations.percent_annotation import PercentAnnotation
from lexnlp.extract.en.percents import get_percents, get_percent_annotations
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


class TestPercentPlain(TestCase):

    def test_percent(self):
        text = "I'm 146.5 percent sure (or just 100%)"
        ds = list(get_percents(text))
        self.assertEqual(2, len(ds))

        ants = list(get_percent_annotations(text))
        self.assertEqual(2, len(ants))
        self.assertEqual('en', ants[0].locale)
        self.assertEqual('percent', ants[0].sign)
        self.assertEqual(146.5, ants[0].amount)

        self.assertEqual('%', ants[1].sign)
        self.assertEqual(100.0, ants[1].amount)

    def test_percent_amount(self):
        text = "30% or more plus"
        ants = list(get_percent_annotations(text))
        self.assertEqual(1, len(ants))
        self.assertEqual(30, ants[0].amount)
        self.assertEqual(Decimal('0.3'), ants[0].fraction)

    def test_percent_fraction(self):
        text = '1/2 %'
        ants = list(get_percent_annotations(text))
        self.assertEqual(1, len(ants))
        self.assertEqual(Decimal('0.005'), ants[0].fraction)

        text = '2 ⅗ percent'
        ants = list(get_percent_annotations(text))
        self.assertEqual(1, len(ants))
        self.assertEqual(Decimal('0.026'), ants[0].fraction)

    def test_percent_mix_fraction(self):
        text = '020 ⅗%'
        ants = list(get_percent_annotations(text))
        self.assertEqual(1, len(ants))
        self.assertEqual(Decimal('0.206'), ants[0].fraction)

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_percent_annotations,
            'lexnlp/typed_annotations/en/percent/percents.txt',
            PercentAnnotation)
