__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from unittest import TestCase

from lexnlp.extract.common.annotations.regulation_annotation import RegulationAnnotation
from lexnlp.extract.en.regulations import get_regulations, get_regulation_annotations
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


class TestRegulationsPlain(TestCase):

    def test_regulations(self):
        text = 'test 123 U.S.C § 456, code'
        rs = list(get_regulations(text))
        self.assertEqual(1, len(rs))
        self.assertEqual('United States Code', rs[0][0])
        self.assertEqual('123 USC § 456', rs[0][1])

        rs = list(get_regulations(text, as_dict=True))
        self.assertEqual(1, len(rs))
        self.assertEqual('United States Code', rs[0]['regulation_type'])
        self.assertEqual('123 USC § 456', rs[0]['regulation_code'])

        ants = list(get_regulation_annotations(text))
        self.assertEqual(1, len(ants))
        self.assertEqual('en', ants[0].locale)
        self.assertEqual('123 USC § 456', ants[0].name)
        self.assertEqual('United States Code', ants[0].source)

        start = text.find('123')
        self.assertGreater(ants[0].coords[1], ants[0].coords[0])
        self.assertEqual((start, ants[0].coords[1]), ants[0].coords)

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_regulation_annotations,
            'lexnlp/typed_annotations/en/regulation/regulations.txt',
            RegulationAnnotation)
