__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from unittest import TestCase

from lexnlp.extract.common.annotations.condition_annotation import ConditionAnnotation
from lexnlp.extract.en.conditions import get_condition_annotations
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


class TestConditionsPlain(TestCase):

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_condition_annotations,
            'lexnlp/typed_annotations/en/condition/conditions.txt',
            ConditionAnnotation)
