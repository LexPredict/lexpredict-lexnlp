__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import List
from decimal import Decimal
from lexnlp.extract.common.annotations.duration_annotation import DurationAnnotation
from lexnlp.extract.de.durations import get_duration_list, get_duration_annotations
from lexnlp.extract.de.tests.test_amounts import AssertionMixin
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


class TestGetDurations(AssertionMixin):
    def test_duration_prefix(self):
        text = """zur kurzfristigen Betreuung von Kindern im Sinne des § 32 Absatz 1,  die das 14. Lebensjahr noch nicht vollendet haben oder die wegen einer vor Vollendung des 25. Lebensjahres eingetretenen körperlichen, geistigen oder seelischen Behinderung außerstande sind, sich selbst zu unterhalten oder pflegebedürftigen Angehörigen des Arbeitnehmers, wenn die Betreuung aus zwingenden und beruflich veranlassten Gründen notwendig ist, auch wenn sie im privaten Haushalt des Arbeitnehmers stattfindet, soweit die Leistungen 600 Euro im Kalenderjahr nicht übersteigen;"""
        res = get_duration_list(text=text)
        self.assertCountEqual(res, [{'location_start': 77,
                                     'location_end': 92,
                                     'source_text': '14. Lebensjahr',
                                     'unit_name_local': 'jahr',
                                     'unit_name': 'year',
                                     'unit_prefix': 'lebens',
                                     'amount': 14.0,
                                     'amount_days': 5110.0},
                                    {'location_start': 159,
                                     'location_end': 176,
                                     'source_text': '25. Lebensjahres',
                                     'unit_name_local': 'jahres',
                                     'unit_name': 'year',
                                     'unit_prefix': 'lebens',
                                     'amount': 25.0,
                                     'amount_days': 9125.0},
                                    {'location_start': 525,
                                     'location_end': 538,
                                     'source_text': 'Kalenderjahr',
                                     'unit_name_local': 'jahr',
                                     'unit_name': 'year',
                                     'unit_prefix': 'kalender',
                                     'amount': 1,
                                     'amount_days': 365}])

    def test_written_duration(self):
        text = 'seit fünfundzwanzig Jahren'
        res = get_duration_list(text=text)
        self.assertCountEqual(res, [{'location_start': 4,
                                     'location_end': 26,
                                     'source_text': ' fünfundzwanzig Jahren',
                                     'unit_name_local': 'jahren',
                                     'unit_name': 'year',
                                     'unit_prefix': '',
                                     'amount': 25,
                                     'amount_days': 9125}])

        ants = list(get_duration_annotations(text=text))
        self.assertEqual((4, 26), ants[0].coords)
        self.assertEqual('fünfundzwanzig Jahren', ants[0].text.strip())
        self.assertEqual('jahren', ants[0].duration_type)
        self.assertEqual('year', ants[0].duration_type_en)
        self.assertEqual('', ants[0].prefix)
        self.assertEqual(Decimal(25), ants[0].amount)
        self.assertEqual(Decimal(9125), ants[0].duration_days)

    def test_complex_durations(self):
        text = 'Vier Wochen, 3 Tage und 151 Sekunden.'
        ants = list(get_duration_annotations(text=text))
        self.assertEqual(1, len(ants))
        self.assertEqual(Decimal('31.0017'), ants[0].duration_days)
        self.assertTrue(ants[0].is_complex)
        self.assertEqual('second', ants[0].duration_type_en)
        self.assertEqual('sekunden', ants[0].duration_type)

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_ordered_durations,
            'lexnlp/typed_annotations/de/duration/durations.txt',
            DurationAnnotation)


def get_ordered_durations(text: str) -> List[DurationAnnotation]:
    ants = list(get_duration_annotations(text))
    ants.sort(key=lambda a: a.coords[0])
    return ants
