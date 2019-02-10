from lexnlp.extract.de.durations import get_durations
from lexnlp.extract.de.tests.test_amounts import AssertionMixin


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.4"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestGetPercents(AssertionMixin):
    def test_duration_prefix(self):
        text = """zur kurzfristigen Betreuung von Kindern im Sinne des § 32 Absatz 1,  die das 14. Lebensjahr noch nicht vollendet haben oder die wegen einer vor Vollendung des 25. Lebensjahres eingetretenen körperlichen, geistigen oder seelischen Behinderung außerstande sind, sich selbst zu unterhalten oder pflegebedürftigen Angehörigen des Arbeitnehmers, wenn die Betreuung aus zwingenden und beruflich veranlassten Gründen notwendig ist, auch wenn sie im privaten Haushalt des Arbeitnehmers stattfindet, soweit die Leistungen 600 Euro im Kalenderjahr nicht übersteigen;"""
        res = list(get_durations(text))
        self.assertEqual(res, [{'location_start': 77,
                                'location_end': 92,
                                'source_text': '14. Lebensjahr',
                                'unit_name_local': 'jahr',
                                'unit_name': 'year',
                                'unit_prefix': 'lebens',
                                'amount': 14.0,
                                'amount_days': 5110.0},
                               {'location_start': 159,
                                'location_end': 176,
                                'source_text': '25. Lebensjahres',
                                'unit_name_local': 'jahr',
                                'unit_name': 'year',
                                'unit_prefix': 'lebens',
                                'amount': 25.0,
                                'amount_days': 9125.0},
                               {'location_start': 525,
                                'location_end': 538,
                                'source_text': 'Kalenderjahr',
                                'unit_name_local': 'jahr',
                                'unit_name': 'year',
                                'unit_prefix': 'kalender',
                                'amount': 1,
                                'amount_days': 365}])

    def test_written_duration(self):
        text = 'seit fünfundzwanzig Jahren'
        res = list(get_durations(text))
        self.assertEqual(res, [{'location_start': 4,
                                'location_end': 26,
                                'source_text': ' fünfundzwanzig Jahren',
                                'unit_name_local': 'jahr',
                                'unit_name': 'year',
                                'unit_prefix': '',
                                'amount': 25,
                                'amount_days': 9125}])
