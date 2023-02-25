__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from unittest import TestCase

from lexnlp.extract.common.annotations.ssn_annotation import SsnAnnotation
from lexnlp.extract.en.pii import get_ssns, get_ssn_annotations
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


class TestSsnPlain(TestCase):

    def test_ssn(self):
        text = "Somewhere in the form I filled out my SSN (123-45-6789) number"
        ds = list(get_ssns(text))
        self.assertEqual(1, len(ds))

        ants = list(get_ssn_annotations(text))
        self.assertEqual(1, len(ds))
        self.assertEqual('en', ants[0].locale)
        self.assertEqual('123-45-6789', ants[0].number)

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_ssn_annotations,
            'lexnlp/typed_annotations/en/ssn/ssn.txt',
            SsnAnnotation)
