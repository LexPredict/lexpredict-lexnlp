__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from unittest import TestCase

from lexnlp.extract.common.annotations.definition_annotation import DefinitionAnnotation
from lexnlp.extract.common.tests.definitions_text_annotator \
    import annotate_definitions_text
from lexnlp.extract.de.definitions import get_definition_list, get_definitions, get_definition_annotations, \
    get_definition_annotation_list
from lexnlp.tests.utility_for_testing import load_resource_document
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


class TestParseDeutscheDefinitions(TestCase):

    def test_parse_de_definitions_im_sinne(self):
        text = " Vermögensgegenstände im Sinne dieses Gesetzes sind unbewegliches Vermögen im Sinne des Absatzes 8, " + \
               "ferner zu dessen Bewirtschaftung erforderliche Gegenstände sowie Bankguthaben, Geldmarktinstrumente, " + \
               "Forderungen und Verbindlichkeiten, die aus der Nutzung oder Veräußerung des unbeweglichen Vermögens " + \
               "stammen oder zum Zwecke der Wertsicherung, Bewirtschaftung oder Bestandsveränderung dieser " + \
               "Vermögensgegenstände bereitgehalten, eingegangen oder begründet werden, sowie Beteiligungen an " + \
               "Immobilienpersonengesellschaften, Auslandsobjektgesellschaften, REIT-Dienstleistungsgesellschaften " +\
               "sowie Kapitalgesellschaften im Sinne des § 1 Abs. 1 Nr. 5"

        ret = get_definition_annotation_list(text)
        self.assertGreater(len(ret), 0)
        precise_matches = [x for x in ret
                           if x.name.strip(' "') == "Vermögensgegenstände"]
        self.assertGreater(len(precise_matches), 0)

    def test_parse_de_definitions_quoted(self):
        text = """   "Moderne Anatomie Mensch": ein Mensch eines modernen Typs"""
        ret = get_definition_annotation_list(text, 'ru')
        def_name = ret[0].name.strip(' "')
        self.assertEqual("Moderne Anatomie Mensch", def_name)
        self.assertEqual("ru", ret[0].locale)

        items = list(get_definitions(text))
        self.assertEqual("Moderne Anatomie Mensch",
                         items[0]["tags"]["Extracted Entity Definition Name"].strip(' "'))

    def test_parse_de_definitions_ist_jeder(self):
        text = " ist Diensteanbieter jede natürliche oder juristische Person, die eigene oder fremde " +\
               "Telemedien zur Nutzung bereithält oder den Zugang zur Nutzung vermittelt; "
        ret = get_definition_annotation_list(text)
        def_name = ret[0].name.strip(' "')
        self.assertEqual("Diensteanbieter", def_name)
        self.assertEqual("de", ret[0].locale)

        text = """ sind Diensteanbieter jede natürliche oder juristische Person """
        ret = get_definition_annotation_list(text)
        def_name = ret[0].name.strip(' "')
        self.assertEqual("Diensteanbieter", def_name)

    def test_parse_de_definitions_simple(self):
        text = load_resource_document('lexnlp/extract/de/sample_de_definitions01.txt', 'utf-8')
        ret = get_definition_annotation_list(text)
        self.assertGreater(len(ret), 5)

        start = ret[0].coords[0]
        end = ret[0].coords[1]
        def_name = ret[0].name
        self.assertTrue("Diensteanbieter" in def_name)
        definition = text[start:end]
        self.assertTrue(def_name in definition)
        annotate_definitions_text(text, ret, 'output/de_definitions_01.html')

    def test_parse_for_clear_def_name(self):
        text = "(3b) Ordnungswidrig handelt, wer als Mitglied des Aufsichtsrats oder als Mitglied eines " + \
               "Prüfungsausschusses einer Gesellschaft, die kapitalmarktorientiert im Sinne des § 264d des " + \
               "Handelsgesetzbuchs, die CRR-Kreditinstitut im Sinne des § 1 Absatz 3d Satz 1 des Kreditwesengesetzes, " + \
               "mit Ausnahme der in § 2 Absatz 1 Nummer 1 und 2 des Kreditwesengesetzes genannten Institute, oder " + \
               "die Versicherungsunternehmen ist im Sinne des Artikels 2 Absatz 1 der Richtlinie 91/674/EWG des Rates vom 19."
        ret = get_definition_list(text)
        assert len(ret) > 0

    def test_parse_de_definitions_tail_break(self):
        text = "Vermögensgegenstände im Sinne dieses Gesetzes sind unbewegliches Vermögen im Sinne des Absatzes 8, " +\
               "ferner zu dessen Bewirtschaftung erforderliche Gegenstände sowie Bankguthaben, " +\
               "Geldmarktinstrumente, Forderungen und Verbindlichkeiten, die aus der Nutzung oder " +\
               "Veräußerung des unbeweglichen Vermögens stammen oder zum Zwecke der Wertsicherung, " +\
               "Bewirtschaftung oder Bestandsveränderung dieser Vermögensgegenstände bereitgehalten, " +\
               "eingegangen oder begründet werden, sowie Beteiligungen an Immobilienpersonengesellschaften, " +\
               "Auslandsobjektgesellschaften, REIT-Dienstleistungsgesellschaften sowie Kapitalgesellschaften " +\
               "im Sinne des § 1 Abs. 1 Nr. 5"
        ret = get_definition_annotation_list(text)
        self.assertGreater(len(ret), 0)
        # TODO: sind unbewegliches Vermögen im Sinne is a false positive
        names = {d.name.strip(' "'): True for d in ret}
        self.assertEqual(True, "Vermögensgegenstände" in names)

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_definition_annotations,
            'lexnlp/typed_annotations/de/definition/definitions.txt',
            DefinitionAnnotation)
