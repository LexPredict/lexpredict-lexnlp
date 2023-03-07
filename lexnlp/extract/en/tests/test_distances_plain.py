__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from unittest import TestCase

from lexnlp.extract.common.annotations.distance_annotation import DistanceAnnotation
from lexnlp.extract.en.distances import get_distances, get_distance_annotations
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


class TestDistancesPlain(TestCase):

    def test_distances_digits(self):
        text = 'Today I ran 8 miles.'
        ds = list(get_distances(text))
        self.assertEqual(1, len(ds))

        ant = list(get_distance_annotations(text))[0]
        self.assertEqual((12, 20), ant.coords)
        cite = ant.get_cite()
        self.assertEqual('/en/distance/8.0/mile', cite)

    def test_distances_words(self):
        text = 'Today I ran eight kilometers.'
        ds = list(get_distances(text))
        self.assertEqual(1, len(ds))

        ant = list(get_distance_annotations(text))[0]
        self.assertEqual((11, 29), ant.coords)
        cite = ant.get_cite()
        self.assertEqual('/en/distance/8.0/kilometer', cite)

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_distance_annotations,
            'lexnlp/typed_annotations/en/distance/distances.txt',
            DistanceAnnotation)
