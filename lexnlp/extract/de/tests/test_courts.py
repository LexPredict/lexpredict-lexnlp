from unittest import TestCase
from lexnlp.extract.de.courts import setup_de_parser
from lexnlp.tests.test_utils import load_resource_document


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.4"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestParseDeCourts(TestCase):
    def test_parse_empty_text(self):
        parser = setup_de_parser()
        ret = parser.parse('')
        self.assertEqual(0, len(ret))
        ret = parser.parse("""

         """)
        self.assertEqual(0, len(ret))

    def test_parse_simply_phrase(self):
        parser = setup_de_parser()
        text = "Bei dir läuft, deine Boys rauchen Joints vor der Kamera Bundesverfassungsgericht."
        ret = parser.parse(text)
        self.assertEqual(1, len(ret))

    def test_parse_precise_and_type_only(self):
        parser = setup_de_parser()
        text = "Bei dir läuft, deine Verfassungsgerichtshof des Freistaates Sachsen rauchen Joints vor der Kamera. Amtsgerichte - arbeit nicht frei."
        ret = parser.parse(text)
        self.assertEqual(2, len(ret))
        self.assertEqual('Verfassungsgerichtshof des Freistaates Sachsen',
                         ret[0]["tags"]["Extracted Entity Court Name"])
        self.assertEqual('Amtsgerichte',
                         ret[1]["tags"]["Extracted Entity Court Name"])

    def test_load_courts(self):
        parser = setup_de_parser()
        text = load_resource_document(
            'lexnlp/extract/de/sample_de_courts01.txt', 'utf-8')
        ret = parser.parse(text)
        self.assertEqual(4, len(ret))

    def test_parse_baden_baden_court(self):
        parser = setup_de_parser()
        text = " vom Amtsgericht Stuttgart als zentralem Mahngericht im automatisierten Verfahren bearbeitet, Amtsgerichte  Pforzheim"
        ret = parser.parse(text)
        self.assertEqual(2, len(ret))

    def test_load_courts_with_toponims(self):
        parser = setup_de_parser()
        text = load_resource_document(
            'lexnlp/extract/de/sample_de_courts02.txt', 'utf-8')
        ret = parser.parse(text)
        self.assertEqual(2, len(ret))
        jurisdiction = ret[0]["tags"]["Extracted Entity Court Jurisdiction"]
        self.assertEqual("Federal", jurisdiction)
