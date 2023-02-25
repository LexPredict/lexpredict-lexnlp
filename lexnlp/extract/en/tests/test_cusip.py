__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from lexnlp.extract.common.annotations.cusip_annotation import CusipAnnotation
from lexnlp.extract.en.cusip import get_cusip_list, get_cusip_annotations
from lexnlp.extract.de.tests.test_amounts import AssertionMixin
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


class TestGetCUSIP(AssertionMixin):
    def test_correct_cases(self):
        text = "This is 837649128"
        res = get_cusip_list(text)
        self.assertEqual(res, [{'location_start': 8,
                                'location_end': 17,
                                'text': '837649128',
                                'issuer_id': '837649',
                                'issue_id': '12',
                                'checksum': 8,
                                'ppn': False,
                                'tba': None,
                                'internal': False}])
        text = "This is 392690QT3."
        res = get_cusip_list(text)
        self.assertEqual(res, [{'location_start': 8,
                                'location_end': 17,
                                'text': '392690QT3',
                                'issuer_id': '392690',
                                'issue_id': 'QT',
                                'checksum': 3,
                                'ppn': False,
                                'tba': None,
                                'internal': False}])
        text = "This is 39299ZQT0 code"
        res = get_cusip_list(text)
        self.assertEqual(res, [{'location_start': 8,
                                'location_end': 17,
                                'text': '39299ZQT0',
                                'issuer_id': '39299Z',
                                'issue_id': 'QT',
                                'checksum': 0,
                                'ppn': False,
                                'tba': None,
                                'internal': True}])
        text = "This is 39298#QT5 code"
        res = get_cusip_list(text)
        self.assertEqual(res, [{'location_start': 8,
                                'location_end': 17,
                                'text': '39298#QT5',
                                'issuer_id': '39298#',
                                'issue_id': 'QT',
                                'checksum': 5,
                                'ppn': True,
                                'tba': None,
                                'internal': False}])
        text = "This is TBA 12F123454 code"
        res = get_cusip_list(text)
        self.assertEqual(res, [{'location_start': 12,
                                'location_end': 21,
                                'text': '12F123454',
                                'issuer_id': '12F123',
                                'issue_id': '45',
                                'checksum': 4,
                                'internal': False,
                                'tba': {'product_code': '12',
                                        'mortgage_type': 'F',
                                        'coupon': '123',
                                        'maturity': '4',
                                        'settlement_month': '5',
                                        'checksum': '4',
                                        'settlement_month_name': 'May'},
                                'ppn': False}])

    def test_wrong_cases(self):
        text = "This is awesome but incorrect 39299ZQT1 code"
        res = get_cusip_list(text)
        self.assertEqual(res, [])
        text = "This is wrong 3929#ZQT8 code"
        res = get_cusip_list(text)
        self.assertEqual(res, [])

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_cusip_annotations,
            'lexnlp/typed_annotations/en/cusip/cusips.txt',
            CusipAnnotation)
