__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import codecs
import os
from unittest import TestCase

from typing import Generator

from lexnlp.extract.common.base_path import lexnlp_test_path
from lexnlp.extract.common.annotations.copyright_annotation import CopyrightAnnotation
from lexnlp.extract.en.copyright import get_copyrights, get_copyright_annotations
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


class TestCopyrightPlain(TestCase):

    def test_copyrights(self):
        text = '(C)Maverick(R) International Processing Services, Inc. 1999'
        cs = list(get_copyrights(text))
        self.assertEqual(1, len(cs))

        ant = list(get_copyright_annotations(text))[0]
        self.assertEqual((0, 58), ant.coords)
        cite = ant.get_cite()
        self.assertEqual('/en/copyright/Maverick/1999', cite)

    def test_text_coords(self):
        text = """
The provisions contained in Sections 2   through 36, inclusive, which 
appear after the signature lines below, are a part of this Lease and are 
incorporated in this Lease by reference. The (C)Tenant(R) and the Landlord have 
executed or caused to be executed this Lease on the dates shown below their 
signatures, to be effective as of the date set forth above.
        """
        ant = list(get_copyright_annotations(text))[0]
        start = text.find('(C)Tenant')
        self.assertEqual(start, ant.coords[0])

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_copyright_verbose_annotations,
            'lexnlp/typed_annotations/en/copyright/copyrights.txt',
            CopyrightAnnotation)

    def test_big_file(self):
        file_path = os.path.join(lexnlp_test_path,
                                 'lexnlp/extract/en/copyrights/bigfile.txt')
        with codecs.open(file_path, encoding='utf-8', mode='r') as of:
            text = of.read()
        cs = []
        for part in text.split('\n\n'):
            for ant in get_copyright_annotations(part):
                cs.append(ant)
        self.assertEqual(3, len(cs))


def get_copyright_verbose_annotations(text: str) -> \
        Generator[CopyrightAnnotation, None, None]:
    yield from get_copyright_annotations(text, return_sources=True)
