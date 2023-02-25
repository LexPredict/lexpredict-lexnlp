__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from unittest import TestCase

from lexnlp.extract.common.annotations.court_annotation import CourtAnnotation
from lexnlp.extract.de.courts import get_court_list, get_court_annotations, get_court_annotation_list
from lexnlp.tests.utility_for_testing import load_resource_document
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


class TestParseDeCourts(TestCase):
    def test_parse_empty_text(self):
        ret = get_court_list('')
        self.assertEqual(0, len(ret))
        ret = get_court_list("""

         """)
        self.assertEqual(0, len(ret))

    def test_parse_simply_phrase(self):
        text = "Bei dir läuft, deine Boys rauchen Joints vor der Kamera Bundesverfassungsgericht."
        ret = get_court_annotation_list(text)
        self.assertEqual(1, len(ret))
        self.assertEqual("de", ret[0].locale)
        self.assertEqual("Bundesverfassungsgericht", ret[0].text.strip("' "))

    def test_parse_precise_and_type_only(self):
        text = "Bei dir läuft, deine Verfassungsgerichtshof des Freistaates Sachsen rauchen Joints vor der Kamera. Amtsgerichte - arbeit nicht frei."
        ret = get_court_list(text)
        self.assertEqual(2, len(ret))
        self.assertEqual('Verfassungsgerichtshof des Freistaates Sachsen',
                         ret[0]["tags"]["Extracted Entity Court Name"])
        self.assertEqual('Amtsgerichte',
                         ret[1]["tags"]["Extracted Entity Court Name"])

    def test_load_courts(self):
        text = load_resource_document('lexnlp/extract/de/sample_de_courts01.txt', 'utf-8')
        ret = get_court_annotation_list(text, "y")
        self.assertEqual(4, len(ret))
        self.assertEqual("y", ret[0].locale)

    def test_parse_baden_baden_court(self):
        text = " vom Amtsgericht Stuttgart als zentralem Mahngericht im automatisierten Verfahren bearbeitet, Amtsgerichte  Pforzheim"
        ret = get_court_list(text)
        self.assertEqual(2, len(ret))

    def test_load_courts_with_toponyms(self):
        text = load_resource_document('lexnlp/extract/de/sample_de_courts02.txt', 'utf-8')
        ret = get_court_list(text)
        self.assertEqual(2, len(ret))
        jurisdiction = ret[0]["tags"]["Extracted Entity Court Jurisdiction"]
        self.assertEqual("Federal", jurisdiction)

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_court_annotations,
            'lexnlp/typed_annotations/de/court/courts.txt',
            CourtAnnotation)
