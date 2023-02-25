__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from unittest import TestCase

from typing import List

from lexnlp.extract.common.annotations.copyright_annotation import CopyrightAnnotation
from lexnlp.extract.es.copyrights import get_copyright_list, get_copyrights, get_copyright_annotations, \
    get_copyright_annotation_list
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


class TestParseEsCourts(TestCase):
    def test_parse_empty_text(self):
        ret = get_copyright_list('')
        self.assertEqual(0, len(ret))
        ret = get_copyright_list("""

         """)
        self.assertEqual(0, len(ret))

    def test_parse_simply_phrase(self):
        text = "Website BBC Mundo © 1996 – 2019   "
        ret = get_copyright_annotation_list(text)
        self.assertEqual(1, len(ret), 'test_parse_simply_phrase failed')
        self.assertEqual((18, 34), ret[0].coords)
        self.assertEqual(1996, ret[0].year_start)

    def test_two_symbols(self):
        text = "Copyright © 2019 BBC"
        ret = get_copyright_annotation_list(text)
        self.assertEqual(1, len(ret), 'test_two_symbols failed')
        self.assertEqual('es', ret[0].locale)

        ret = list(get_copyrights(text))
        self.assertEqual(1, len(ret), 'test_two_symbols failed')

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_verbose_copyright_annotations,
            'lexnlp/typed_annotations/es/copyright/copyrights.txt',
            CopyrightAnnotation)


def get_verbose_copyright_annotations(text: str) -> List[CopyrightAnnotation]:
    return list(get_copyright_annotations(text, return_sources=True))
