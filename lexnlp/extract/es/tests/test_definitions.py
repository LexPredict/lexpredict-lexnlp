from unittest import TestCase

from lexnlp.extract.common.tests.definitions_text_annotator import annotate_definitions_text
from lexnlp.extract.es.definitions import make_es_definitions_parser
from lexnlp.tests.test_utils import load_resource_document

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.4"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestParseSpanishDefinitions(TestCase):
    def test_parse_es_def_semicolon(self):
        parser = make_es_definitions_parser()
        text = """
        Me gusta tocar la guitarra.
        "El ser humano": una anatomía moderna humana.
        Me gusta cantar el sol"""

        ret = parser.parse(text)
        assert len(ret) == 1
        name = ret[0]["tags"]["Extracted Entity Definition Name"]
        self.assertEqual("El ser humano", name.strip('"'))

    def test_parse_es_def_quotes(self):
        parser = make_es_definitions_parser()
        text = "Mariachi me acompaña cuando canto mi canción. En este acuerdo, el término \"Software\" se refiere a: (i) el programa informático y todos sus componentes;"

        ret = parser.parse(text)
        assert len(ret) == 1
        name = ret[0]["tags"]["Extracted Entity Definition Name"]
        self.assertEqual("Software", name.strip('"'))

    def test_grab_just_quoted_words(self):
        parser = make_es_definitions_parser()
        text = """(en adelante, "ESET" o "el Proveedor") y usted"""
        ret = parser.parse(text)
        assert len(ret) == 2

    def test_parse_de_definitions_simple(self):
        parser = make_es_definitions_parser()
        text = load_resource_document('lexnlp/extract/es/definitions/eula.txt', 'utf-8')
        ret = parser.parse(text)
        assert len(ret) > 4
        annotate_definitions_text(text, ret, 'output/es_definitions_01.html')
