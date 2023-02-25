__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import List
from decimal import Decimal
from lexnlp.extract.common.annotations.percent_annotation import PercentAnnotation
from lexnlp.extract.de.percents import get_percents, get_percent_annotations
from lexnlp.extract.de.tests.test_amounts import AssertionMixin
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


class TestGetPercents(AssertionMixin):
    def test_percent_prefix(self):
        text = 'sie weisen einen vorhandenen Alkoholgehalt von mehr' \
               ' als 15 Volumenprozent bis 18 Volumenprozent auf, sind ohne....'
        res = list(get_percents(text))
        self.assertEqual(res, [{'location_start': 56,
                                'location_end': 74,
                                'source_text': '15 Volumenprozent',
                                'unit_name': 'prozent',
                                'amount': 15.0,
                                'real_amount': 15.0},
                               {'location_start': 78,
                                'location_end': 96,
                                'source_text': '18 Volumenprozent',
                                'unit_name': 'prozent',
                                'amount': 18.0,
                                'real_amount': 18.0}])

    def test_written_percent(self):
        text = 'Dieses Einkommen macht zwanzig Prozent des Gesamteinkommens aus'
        res = list(get_percents(text))
        self.assertEqual(res, [{'location_start': 22,
                                'location_end': 39,
                                'source_text': ' zwanzig Prozent',
                                'unit_name': 'prozent',
                                'amount': 20,
                                'real_amount': 20}])
        text = 'Dieses Einkommen macht zwanzig % des Gesamteinkommens aus'
        res = list(get_percents(text))
        self.assertEqual(res, [{'location_start': 22,
                                'location_end': 33,
                                'source_text': ' zwanzig %',
                                'unit_name': '%',
                                'amount': 20,
                                'real_amount': 20}])

    def test_annotations(self):
        text = 'Dieses Einkommen macht zwanzig Prozent des Gesamteinkommens aus'
        res = list(get_percent_annotations(text))
        self.assertEqual(1, len(res))
        self.assertEqual((22, 39), res[0].coords)
        self.assertEqual('zwanzig Prozent', res[0].text.strip())
        self.assertEqual('prozent', res[0].sign)
        self.assertEqual(Decimal(20), res[0].amount)
        self.assertEqual(Decimal(20), res[0].fraction)

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_ordered_percent_annotations,
            'lexnlp/typed_annotations/de/percent/percents.txt',
            PercentAnnotation)


def get_ordered_percent_annotations(text: str) -> List[PercentAnnotation]:
    ants = list(get_percent_annotations(text))
    ants.sort(key=lambda a: a.coords[0])
    return ants
