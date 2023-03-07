__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from unittest import TestCase

from lexnlp.extract.common.annotations.duration_annotation import DurationAnnotation
from lexnlp.extract.en.durations import get_durations, get_duration_annotations, get_duration_annotations_list
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


class TestDurationsPlain(TestCase):

    def test_durations_digits(self):
        text = "I'd been waiting for 15 minutes before you finally came."
        ds = list(get_durations(text))
        self.assertEqual(1, len(ds))

        ant = list(get_duration_annotations(text))[0]
        self.assertEqual((21, 32), ant.coords)
        cite = ant.get_cite()
        self.assertEqual('/en/duration/15.0/minute', cite)

    def test_durations_days(self):
        text = "I'd been waiting for 1440 minutes before you finally came."
        ant = list(get_duration_annotations(text))[0]
        self.assertEqual(1.0, ant.duration_days)
        cite = ant.get_cite()
        self.assertEqual('/en/duration/1440.0/minute', cite)

    def test_a_and_b(self):
        text = '5 years and 6 months'
        ants = get_duration_annotations_list(text)
        self.assertEqual(1, len(ants))
        self.assertEqual(2005, ants[0].duration_days)
        self.assertEqual('month', ants[0].duration_type)
        self.assertTrue(ants[0].is_complex)

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_duration_annotations,
            'lexnlp/typed_annotations/en/duration/durations.txt',
            DurationAnnotation)
