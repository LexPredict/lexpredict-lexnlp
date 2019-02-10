from unittest import TestCase
from lexnlp.extract.es.courts import get_courts, setup_es_parser


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.4"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestParseEsCourts(TestCase):

    def test_parse_empty_text(self):
        parser = setup_es_parser()
        ret = parser.parse('')
        self.assertEqual(0, len(ret))
        ret = parser.parse("""

         """)
        self.assertEqual(0, len(ret))

    def test_parse_full_entry(self):
        parser = setup_es_parser()
        text = "El actual Tribunal Superior de Justicia de Madrid fue creado en 1985 a partir del artículo 26 de la Ley Orgánica del Poder Judicial, constituyéndose el 23 de mayo de 1989."

        ret = parser.parse(text)
        self.assertEqual(1, len(ret))
        court_name = ret[0]["tags"]["Extracted Entity Court Name"]
        self.assertEqual('Tribunal Superior de Justicia de Madrid', court_name)

    def test_parse_partial_entry(self):
        parser = setup_es_parser()
        text = "Sembré una flor sin interés. Yo la sembré para ver el Tribunal Superior, al volver ya estaba seca y ya no quizo retoñar."
        ret = parser.parse(text)
        self.assertEqual(1, len(ret))
        court_name = ret[0]["tags"]["Extracted Entity Court Name"]
        self.assertEqual('Tribunal Superior', court_name)
