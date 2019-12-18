from unittest import TestCase

from lexnlp.extract.common.annotations.amount_annotation import AmountAnnotation
from lexnlp.extract.en.amounts import get_amounts, get_amount_annotations
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestAmountsPlain(TestCase):

    def test_amounts(self):
        text = """
        2. Amendment to Interest Rate. Beginning on February 1, 1998, and
                continuing until July 18, 2002, which is the fifth anniversary of the Loan
                conversion date, interest shall be fixed at an annual rate of 7.38%, which rate
                is equal to 200 basis points above the Bank's five-year ""Treasury Constant
                Rate"" in effect on January 23, 1998. In accordance with the Agreement, the
                interest rate shall be adjusted again on July 18, 2002.
        """
        amts = list(get_amounts(text))
        str_vals = ', '.join([str(f) for f in amts])
        self.assertEqual(
            '2.0, 1.0, 1998.0, 18.0, 2002.0, 5, 7.38, 200.0, 5, 23.0, 1998.0, 18.0, 2002.0',
            str_vals)

    def test_fraction_symbol(self):
        text = "1½ of apple"
        amts = list(get_amount_annotations(text))
        self.assertEqual(1, len(amts))
        self.assertEqual(1.5, amts[0].value)

        text = '2 ⅗'
        amts = list(get_amount_annotations(text))
        self.assertEqual(1, len(amts))
        self.assertEqual(2.6, amts[0].value)

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_amount_annotations,
            'lexnlp/typed_annotations/en/amount/amounts.txt',
            AmountAnnotation)
