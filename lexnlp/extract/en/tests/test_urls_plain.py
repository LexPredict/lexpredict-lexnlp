from unittest import TestCase

from lexnlp.extract.common.annotations.url_annotation import UrlAnnotation
from lexnlp.extract.en.urls import get_urls, get_url_annotations
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestRatiosPlain(TestCase):

    def test_ratios(self):
        text = "I've been banned on www.google.com :("
        ds = list(get_urls(text))
        self.assertEqual(1, len(ds))
        self.assertEqual('www.google.com', ds[0])

        ants = list(get_url_annotations(text))
        self.assertEqual(1, len(ds))
        self.assertEqual('en', ants[0].locale)
        self.assertEqual('www.google.com', ants[0].url)

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_url_annotations,
            'lexnlp/typed_annotations/en/url/urls.txt',
            UrlAnnotation)
