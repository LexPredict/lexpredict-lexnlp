from lexnlp.extract.en.cusip import get_cusip_list
from lexnlp.extract.de.tests.test_amounts import AssertionMixin


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


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
