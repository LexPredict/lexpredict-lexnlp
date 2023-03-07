__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from unittest import TestCase

from lexnlp.extract.common.annotations.court_citation_annotation import CourtCitationAnnotation
from lexnlp.extract.de.court_citations import get_court_citation_list, get_court_citations, \
    get_court_citation_annotations
from lexnlp.tests.utility_for_testing import load_resource_document
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


class TestCourtCitationsParser(TestCase):
    def test_parse_empty(self):
        text = ''
        items = get_court_citation_list(text)
        self.assertEqual(0, len(items))

        text = """

        """
        items = get_court_citation_list(text)
        self.assertEqual(0, len(items))

    def test_find_in_braces(self):
        text = """
        Mit Einreichung der Körperschaftsteuererklärung für das Jahr 2006 im Februar 2008 beantragte die Klägerin unter Bezugnahme auf das Schreiben des Bundesministeriums der Finanzen (BMF) vom 27.3.2003 IV A 6-S 2140-8/03 (BStBl I 2003, 240; - Sanierungserlass -), die Körperschaftsteuer gemäß § 163 der Abgabenordnung (AO) aus Billigkeitsgründen abweichend festzusetzen.
        """
        items = get_court_citation_list(text)
        self.assertEqual(1, len(items))
        self.assertEqual('Bundessteuerblatt (sonstige gebräuchliche Verwendung)', items[0].name)
        self.assertEqual('BStBl I 2003, 240', items[0].text)
        self.assertEqual('BStBl I 2003', items[0].short_name)

        text = """
        Die Festsetzung einer Steuer ist aus (im Streitfall allein streitigen) sachlichen Gründen unbillig, wenn sie zwar dem Wortlaut des Gesetzes entspricht, aber den Wertungen des Gesetzes zuwiderläuft (vgl. Urteile des Bundesfinanzhofs - BFH - vom 4.6.2014 I R 21/13, BFHE 246, 130, BStBl II 2015, 293, Rz 10; BFH-Beschluss vom 12.7.2017 VI R 36/15, BFHE 258, 151, BStBl II 2017, 979)
        """
        items = get_court_citation_list(text)
        self.assertEqual(2, len(items))

    def test_find_beyond_braces(self):
        text = """
        Der IV. Senat des BFH hat im Urteil in BFHE 238, 518, BStBl II 2013, 505 ebenfalls einen Anspruch auf eine Billigkeitsmaßnahme verneint, obwohl der dortige Gewinn auf einem Forderungsverzicht beruhte, durch den der dortigen Klägerin keine Liquidität zugeflossen war.
        """
        items = get_court_citation_list(text)
        self.assertEqual(2, len(items))

    def test_parse(self):
        text = """
                Mit Einreichung der Körperschaftsteuererklärung für das Jahr 2006 im Februar 2008 beantragte die Klägerin unter Bezugnahme auf das Schreiben des Bundesministeriums der Finanzen (BMF) vom 27.3.2003 IV A 6-S 2140-8/03 (BStBl I 2003, 240; - Sanierungserlass -), die Körperschaftsteuer gemäß § 163 der Abgabenordnung (AO) aus Billigkeitsgründen abweichend festzusetzen.
                """
        item = get_court_citation_list(text)[0]
        self.assertEqual('court citation', item.record_type)
        self.assertEqual('BStBl I 2003, 240', item.text)
        self.assertEqual("de", item.locale)

        dics = list(get_court_citations(text))
        self.assertEqual("court citation", dics[0]["tags"]["Extracted Entity Type"])
        self.assertEqual("Bundessteuerblatt (sonstige gebräuchliche Verwendung)",
                         dics[0]["tags"]["Extracted Entity Name"].strip("' "))

    def test_long_doc(self):
        text = load_resource_document('lexnlp/extract/de/sample_de_court_citations01.txt', 'utf-8')
        items = get_court_citation_list(text, "xz")
        self.assertEqual(2, len(items))
        self.assertEqual("xz", items[0].locale)

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_court_citation_annotations,
            'lexnlp/typed_annotations/de/court_citation/court_citations.txt',
            CourtCitationAnnotation)
