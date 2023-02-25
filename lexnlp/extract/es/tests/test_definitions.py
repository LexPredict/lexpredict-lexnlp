__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from unittest import TestCase

from lexnlp.extract.common.annotations.definition_annotation import DefinitionAnnotation
from lexnlp.extract.common.tests.definitions_text_annotator import annotate_definitions_text
from lexnlp.extract.es.definitions import make_es_definitions_parser, get_definition_list, get_definition_annotations, \
    get_definition_annotation_list
from lexnlp.tests.utility_for_testing import load_resource_document
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


class TestParseSpanishDefinitions(TestCase):
    def test_parse_es_def_semicolon(self):
        parser = make_es_definitions_parser()
        text = """
        Me gusta tocar la guitarra.
        "El ser humano": una anatomía moderna humana.
        Me gusta cantar el sol"""

        ret = list(parser.parse(text))
        assert len(ret) == 1
        name = ret[0].name
        self.assertEqual("El ser humano", name.strip('"'))

    def test_parse_es_def_quotes(self):
        parser = make_es_definitions_parser()
        text = "Mariachi me acompaña cuando canto mi canción. En este acuerdo, el término \"Software\" se refiere a: (i) el programa informático y todos sus componentes;"

        ret = list(parser.parse(text))
        assert len(ret) == 1
        name = ret[0].name
        self.assertEqual("Software", name.strip('"'))

    def test_grab_just_quoted_words(self):
        text = """(en adelante, "ESET" o "el Proveedor") y usted"""
        ret = get_definition_annotation_list(text, 'ru')
        self.assertEqual(2, len(ret))
        self.assertEqual('ru', ret[1].locale)
        self.assertEqual((0, 37), ret[1].coords)

        self.assertEqual('"el Proveedor"', ret[1].name)
        self.assertEqual('en adelante, "ESET" o "el Proveedor"',
                         ret[1].text.strip(" ()"))

        ret = get_definition_annotation_list(text)
        self.assertEqual('es', ret[1].locale)

    def test_parse_de_definitions_simple(self):
        parser = make_es_definitions_parser()
        text = load_resource_document('lexnlp/extract/es/definitions/eula.txt', 'utf-8')
        ret = list(parser.parse(text))
        self.assertGreater(len(ret), 4)
        annotate_definitions_text(text, ret, 'output/es_definitions_01.html')

    def test_first_word_is(self):
        text = "El tabaquismo es la adicción al tabaco, provocada principalmente."
        parser = make_es_definitions_parser()
        ret = list(parser.parse(text))
        self.assertEqual(1, len(ret))

        text = "Ella está muerta. "    # too few words after 'está'
        ret = list(parser.parse(text))
        self.assertEqual(0, len(ret))

    def test_acronym(self):
        text = "rompió el silencio tras ser despedido del Canal del Fútbol (CDF). "
        parser = make_es_definitions_parser()

        text = "rompió el silencio tras ser despedido del Canal del Fútbol (cdf). "
        ret = list(parser.parse(text))
        self.assertEqual(0, len(ret))

        text = "rompió el silencio tras ser despedido del Canal del Fútbol (F). "
        ret = list(parser.parse(text))
        self.assertEqual(0, len(ret))

        text = "Pico della Mirandola (PDM)"
        ret = list(parser.parse(text))
        self.assertEqual(1, len(ret))

        text = "Pico Della Mirandola (PDM)"
        ret = list(parser.parse(text))
        self.assertEqual(1, len(ret))

        text = "pico della Mirandola (PDM)"
        ret = list(parser.parse(text))
        self.assertEqual(0, len(ret))

        text = "Pico della Mirandola (PM)"
        ret = list(parser.parse(text))
        self.assertEqual(1, len(ret))

        text = "Pico Della Mirandola (PM)"
        ret = list(parser.parse(text))
        self.assertEqual(1, len(ret))

        text = "Pico della questo quello Mirandola (PDM)"
        ret = list(parser.parse(text))
        self.assertEqual(0, len(ret))

        text = "Pico Pico della Mirandola (PPdM)"
        ret = list(parser.parse(text))
        self.assertEqual(1, len(ret))

        text = "Pico Pico della Mirandola (PpdM)"
        ret = list(parser.parse(text))
        self.assertEqual(1, len(ret))

        text = "Pico Pico della Mirandola (Ppdm)"
        ret = list(parser.parse(text))
        self.assertEqual(0, len(ret))

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_definition_annotations,
            'lexnlp/typed_annotations/es/definition/definitions.txt',
            DefinitionAnnotation)
