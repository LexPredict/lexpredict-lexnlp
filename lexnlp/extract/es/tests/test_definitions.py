from unittest import TestCase
from lexnlp.extract.common.tests.definitions_text_annotator import annotate_definitions_text
from lexnlp.extract.es.definitions import make_es_definitions_parser, get_definition_list
from lexnlp.tests.test_utils import load_resource_document

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.6"
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
        name = ret[0].name
        self.assertEqual("El ser humano", name.strip('"'))

    def test_parse_es_def_quotes(self):
        parser = make_es_definitions_parser()
        text = "Mariachi me acompaña cuando canto mi canción. En este acuerdo, el término \"Software\" se refiere a: (i) el programa informático y todos sus componentes;"

        ret = parser.parse(text)
        assert len(ret) == 1
        name = ret[0].name
        self.assertEqual("Software", name.strip('"'))

    def test_grab_just_quoted_words(self):
        text = """(en adelante, "ESET" o "el Proveedor") y usted"""
        ret = get_definition_list(text, 'ru')
        self.assertEqual(2, len(ret))
        self.assertEqual('ru', ret[1].locale)

        ret = get_definition_list(text)
        self.assertEqual('es', ret[1].locale)

    def test_parse_de_definitions_simple(self):
        parser = make_es_definitions_parser()
        text = load_resource_document('lexnlp/extract/es/definitions/eula.txt', 'utf-8')
        ret = parser.parse(text)
        self.assertGreater(len(ret), 4)
        annotate_definitions_text(text, ret, 'output/es_definitions_01.html')

    def test_first_word_is(self):
        text = "El tabaquismo es la adicción al tabaco, provocada principalmente."
        parser = make_es_definitions_parser()
        ret = parser.parse(text)
        self.assertEqual(1, len(ret))

        text = "Ella está muerta. " # too few words after 'está'
        ret = parser.parse(text)
        self.assertEqual(0, len(ret))

    def test_acronym(self):
        text = "rompió el silencio tras ser despedido del Canal del Fútbol (CDF). "
        parser = make_es_definitions_parser()
        #ret = parser.parse(text)
        #self.assertEqual(1, len(ret))

        text = "rompió el silencio tras ser despedido del Canal del Fútbol (cdf). "
        ret = parser.parse(text)
        self.assertEqual(0, len(ret))

        text = "rompió el silencio tras ser despedido del Canal del Fútbol (F). "
        ret = parser.parse(text)
        self.assertEqual(0, len(ret))

        text = "Pico della Mirandola (PDM)"
        ret = parser.parse(text)
        self.assertEqual(1, len(ret))

        text = "Pico Della Mirandola (PDM)"
        ret = parser.parse(text)
        self.assertEqual(1, len(ret))

        text = "pico della Mirandola (PDM)"
        ret = parser.parse(text)
        self.assertEqual(0, len(ret))

        text = "Pico della Mirandola (PM)"
        ret = parser.parse(text)
        self.assertEqual(1, len(ret))

        text = "Pico Della Mirandola (PM)"
        ret = parser.parse(text)
        self.assertEqual(1, len(ret))

        text = "Pico della questo quello Mirandola (PDM)"
        ret = parser.parse(text)
        self.assertEqual(0, len(ret))

        text = "Pico Pico della Mirandola (PPdM)"
        ret = parser.parse(text)
        self.assertEqual(1, len(ret))

        text = "Pico Pico della Mirandola (PpdM)"
        ret = parser.parse(text)
        self.assertEqual(1, len(ret))

        text = "Pico Pico della Mirandola (Ppdm)"
        ret = parser.parse(text)
        self.assertEqual(0, len(ret))
