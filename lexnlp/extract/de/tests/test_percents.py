from lexnlp.extract.de.percents import get_percents
from lexnlp.extract.de.tests.test_amounts import AssertionMixin


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.4"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestGetPercents(AssertionMixin):
    def test_percent_prefix(self):
        text = 'sie weisen einen vorhandenen Alkoholgehalt von mehr' \
               ' als 15 Volumenprozent bis 18 Volumenprozent auf, sind ohne....'
        res = list(get_percents(text))
        self.assertEqual(res, [{'location_start': 56,
                                'location_end': 74,
                                'source_text': '15 Volumenprozent',
                                'unit_name': 'prozent',
                                'amount': 15.0,
                                'real_amount': 15.0},
                               {'location_start': 78,
                                'location_end': 96,
                                'source_text': '18 Volumenprozent',
                                'unit_name': 'prozent',
                                'amount': 18.0,
                                'real_amount': 18.0}])

    def test_written_percent(self):
        text = 'Dieses Einkommen macht zwanzig Prozent des Gesamteinkommens aus'
        res = list(get_percents(text))
        self.assertEqual(res, [{'location_start': 22,
                                'location_end': 39,
                                'source_text': ' zwanzig Prozent',
                                'unit_name': 'prozent',
                                'amount': 20,
                                'real_amount': 20}])
        text = 'Dieses Einkommen macht zwanzig % des Gesamteinkommens aus'
        res = list(get_percents(text))
        self.assertEqual(res, [{'location_start': 22,
                                'location_end': 33,
                                'source_text': ' zwanzig %',
                                'unit_name': '%',
                                'amount': 20,
                                'real_amount': 20}])
