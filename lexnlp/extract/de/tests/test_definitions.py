from unittest import TestCase

from lexnlp.extract.common.tests.definitions_text_annotator import annotate_definitions_text
from lexnlp.extract.de.definitions import make_de_definitions_parser
from lexnlp.tests.test_utils import load_resource_document

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.4"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestParseDeutscheDefinitions(TestCase):

    def test_parse_de_definitions_im_sinne(self):
        parser = make_de_definitions_parser()
        text = " Vermögensgegenstände im Sinne dieses Gesetzes sind unbewegliches Vermögen im Sinne des Absatzes 8, " + \
               "ferner zu dessen Bewirtschaftung erforderliche Gegenstände sowie Bankguthaben, Geldmarktinstrumente, " + \
               "Forderungen und Verbindlichkeiten, die aus der Nutzung oder Veräußerung des unbeweglichen Vermögens " + \
               "stammen oder zum Zwecke der Wertsicherung, Bewirtschaftung oder Bestandsveränderung dieser " + \
               "Vermögensgegenstände bereitgehalten, eingegangen oder begründet werden, sowie Beteiligungen an " + \
               "Immobilienpersonengesellschaften, Auslandsobjektgesellschaften, REIT-Dienstleistungsgesellschaften " +\
               "sowie Kapitalgesellschaften im Sinne des § 1 Abs. 1 Nr. 5"

        ret = parser.parse(text)
        self.assertGreater(len(ret), 0)
        precise_matches = [x for x in ret
                           if x["tags"]["Extracted Entity Definition Name"].strip(' "') == "Vermögensgegenstände"]
        self.assertGreater(len(precise_matches), 0)

    def test_parse_de_definitions_quoted(self):
        parser = make_de_definitions_parser()
        text = """   "Moderne Anatomie Mensch": ein Mensch eines modernen Typs"""
        ret = parser.parse(text)
        def_name = ret[0]['tags']['Extracted Entity Definition Name']
        assert def_name.strip(' "') == "Moderne Anatomie Mensch"

    def test_parse_de_definitions_ist_jeder(self):
        parser = make_de_definitions_parser()
        text = """ ist Diensteanbieter jede natürliche oder juristische Person, die eigene oder fremde Telemedien zur Nutzung bereithält oder den Zugang zur Nutzung vermittelt; """
        ret = parser.parse(text)
        def_name = ret[0]['tags']['Extracted Entity Definition Name']
        assert def_name.strip(' "') == "Diensteanbieter"

        text = """ sind Diensteanbieter jede natürliche oder juristische Person """
        ret = parser.parse(text)
        def_name = ret[0]['tags']['Extracted Entity Definition Name']
        assert def_name.strip(' "') == "Diensteanbieter"

    def test_parse_de_definitions_simple(self):
        parser = make_de_definitions_parser()
        text = load_resource_document('lexnlp/extract/de/sample_de_definitions01.txt', 'utf-8')
        ret = parser.parse(text)
        assert len(ret) > 5

        start = ret[0]['attrs']['start']
        end = ret[0]['attrs']['end']
        def_name = ret[0]['tags']['Extracted Entity Definition Name']
        assert "Diensteanbieter" in def_name
        definition = text[start:end]
        assert def_name in definition
        annotate_definitions_text(text, ret, 'output/de_definitions_01.html')
