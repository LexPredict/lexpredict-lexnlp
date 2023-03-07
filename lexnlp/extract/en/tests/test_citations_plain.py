__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from unittest import TestCase

from lexnlp.extract.common.annotations.citation_annotation import CitationAnnotation
from lexnlp.extract.en.citations import get_citations, get_citation_annotations
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


class TestCitationsPlain(TestCase):

    def test_citations(self):
        text = 'bob lissner v. test 1 F.2d 1, 2-5 (2d Cir., 1982)'
        cs = list(get_citations(text))
        self.assertEqual(1, len(cs))

        ant = list(get_citation_annotations(text))[0]
        cite = ant.get_cite()
        self.assertEqual('/en/citation/1 F.2d 1, 2-5 (2d Cir., 1982)' +
                         '/1/1982/2-5/2d Cir./F.2d', cite)

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_citation_annotations,
            'lexnlp/typed_annotations/en/citation/citations.txt',
            CitationAnnotation)
