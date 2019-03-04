from unittest import TestCase
from lexnlp.extract.de.courts import get_court_list, get_courts
from lexnlp.tests.test_utils import load_resource_document


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestParseDeCourts(TestCase):
    def test_parse_empty_text(self):
        ret = get_court_list('')
        self.assertEqual(0, len(ret))
        ret = get_court_list("""

         """)
        self.assertEqual(0, len(ret))

    def test_parse_simply_phrase(self):
        text = "Bei dir läuft, deine Boys rauchen Joints vor der Kamera Bundesverfassungsgericht."
        ret = get_court_list(text)
        self.assertEqual(1, len(ret))
        self.assertEqual("de", ret[0].locale)
        self.assertEqual("Bundesverfassungsgericht", ret[0].text.strip("' "))

    def test_parse_precise_and_type_only(self):
        text = "Bei dir läuft, deine Verfassungsgerichtshof des Freistaates Sachsen rauchen Joints vor der Kamera. Amtsgerichte - arbeit nicht frei."
        ret = list(get_courts(text))
        self.assertEqual(2, len(ret))
        self.assertEqual('Verfassungsgerichtshof des Freistaates Sachsen',
                         ret[0]["tags"]["Extracted Entity Court Name"])
        self.assertEqual('Amtsgerichte',
                         ret[1]["tags"]["Extracted Entity Court Name"])

    def test_load_courts(self):
        text = load_resource_document(
            'lexnlp/extract/de/sample_de_courts01.txt', 'utf-8')
        ret = get_court_list(text, "y")
        self.assertEqual(4, len(ret))
        self.assertEqual("y", ret[0].locale)

    def test_parse_baden_baden_court(self):
        text = " vom Amtsgericht Stuttgart als zentralem Mahngericht im automatisierten Verfahren bearbeitet, Amtsgerichte  Pforzheim"
        ret = get_court_list(text)
        self.assertEqual(2, len(ret))

    def test_load_courts_with_toponims(self):
        text = load_resource_document(
            'lexnlp/extract/de/sample_de_courts02.txt', 'utf-8')
        ret = list(get_courts(text))
        self.assertEqual(2, len(ret))
        jurisdiction = ret[0]["tags"]["Extracted Entity Court Jurisdiction"]
        self.assertEqual("Federal", jurisdiction)
