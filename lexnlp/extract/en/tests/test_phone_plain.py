__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from unittest import TestCase

from lexnlp.extract.common.annotations.phone_annotation import PhoneAnnotation
from lexnlp.extract.en.pii import get_us_phones, get_us_phone_annotations
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


class TestPhonePlain(TestCase):

    def test_phone(self):
        text = "Dial +1-541-754-3010 in case of murder"
        ds = list(get_us_phones(text))
        self.assertEqual(1, len(ds))

        ants = list(get_us_phone_annotations(text))
        self.assertEqual(1, len(ds))
        self.assertEqual('en', ants[0].locale)
        self.assertEqual('(541) 754-3010', ants[0].phone)

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_us_phone_annotations,
            'lexnlp/typed_annotations/en/phone/phones.txt',
            PhoneAnnotation)
