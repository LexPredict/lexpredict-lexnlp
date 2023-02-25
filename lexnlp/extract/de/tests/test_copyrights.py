__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from unittest import TestCase

# LexNLP
from lexnlp.extract.common.annotations.copyright_annotation import CopyrightAnnotation
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester
from lexnlp.extract.de.copyrights import (
    get_copyright_list,
    get_copyright_annotations,
    get_copyright_annotation_list,
)


class TestParseDeCourts(TestCase):
    """
    siemens.com globale Website © Siemens 1996 – 2019   Impressum   Datenschutz

    © 2019 urheberrecht.de | Alle Angaben ohne Gewähr

    Copyright © Mustervorlage und Vertrag kostenlos: Vorlagen für Beruf und Privat 2019.
    """
    def test_parse_empty_text(self):
        ret = get_copyright_list('')
        self.assertEqual(0, len(ret))
        ret = get_copyright_list("""

         """)
        self.assertEqual(0, len(ret))

    def test_parse_company_afterwards(self):
        text = "Copyright 2019, Siemens"
        ret = get_copyright_annotation_list(text, return_sources=True)
        self.assertEqual(1, len(ret), 'test_parse_wo_company failed')
        self.assertEqual("de", ret[0].locale)
        self.assertEqual("Siemens", ret[0].company)

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_copyright_annotations,
            'lexnlp/typed_annotations/de/copyright/copyrights.txt',
            CopyrightAnnotation)
