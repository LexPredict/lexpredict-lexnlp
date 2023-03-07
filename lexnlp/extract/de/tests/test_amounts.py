__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from decimal import Decimal
from unittest import TestCase
from num2words import num2words

from lexnlp.extract.common.annotations.amount_annotation import AmountAnnotation
from lexnlp.extract.de.amounts import get_amounts, get_amount_annotations
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


def _sort(v):
    return sorted(v, key=lambda i: i['location_start'])


class AssertionMixin(TestCase):

    def assertOneOK(self, num, writ_num):
        parsed_num = list(get_amounts(writ_num))
        self.assertEqual(len(parsed_num), 1)
        self.assertEqual(num, parsed_num[0])

    def assertSortedByLocationListEqual(self, list1, list2):
        self.assertListEqual(_sort(list1), _sort(list2))

    def assertSortedListEqual(self, list1, list2):
        self.assertListEqual(sorted(list(list1)), sorted(list(list2)))


class TestGetAmounts(AssertionMixin):
    """
    Test prepared for lexnlp method get_amounts
    """
    test_nums = (2, 15, 67, 128, 709, 1234, 3005, 16070, 735900, 900100, 999999, 1234567)

    def assertOneOK(self, num, writ_num):
        parsed_num = list(get_amounts(writ_num))
        self.assertEqual(len(parsed_num), 1)
        self.assertEqual(num, parsed_num[0])

    def test_writ_numbers(self):
        for num in self.test_nums:
            writ_num = num2words(num, ordinal=False, lang='de')
            self.assertOneOK(num, writ_num)

    def test_writ_numbers_ord(self):
        for num in self.test_nums:
            writ_num = num2words(num, ordinal=True, lang='de')
            print(num, writ_num)
            self.assertOneOK(num, writ_num)

    def test_writ_half(self):
        self.assertOneOK(6.5, 'sechseinhalb')
        self.assertOneOK(
            2422703.5, 'zwei Millionen vierhundertzweiundzwanzigtausendsiebenhundertdreieinhalb')
        self.assertOneOK(500000, 'eine halbe Million Dollar')
        # TODO: test 'tausendzweihundertvierunddreißig Komma fünf null'

    def test_writ_quarter(self):
        self.assertOneOK(0.75, 'drei viertel')
        self.assertOneOK(1.25, 'eineinviertel Meilen')

    def test_writ_big_number(self):
        self.assertOneOK(1000, 'tausend')
        self.assertOneOK(1234, 'tausendzweihundertvierunddreißig')
        self.assertOneOK(1000000, 'millionen')

    def test_writ_mixed_number(self):
        self.assertOneOK(1000, '1 tausend')
        self.assertOneOK(5000000, '5 millionen')

    def test_non_writ_number(self):
        self.assertOneOK(1000, 'Es sind 1000 Dollar')
        self.assertOneOK(200000, 'Es sind 200 000 EURO')
        self.assertOneOK(0.5, 'Es sind 0,5 vol')
        self.assertOneOK(10123.5, 'Es sind 10 123,5 vol')

    def test_multiple_values_in_string(self):
        text = 'Sein Volumen beträgt 10 Liter und kostet dreißig Dollar'
        self.assertSortedListEqual(list(get_amounts(text)), [10, 30])
        text = 'Dort waren 30 Leute und sie hatten in zwei Fällen 2 Millionen Dollar'
        self.assertSortedListEqual(list(get_amounts(text)), [2, 30, 2000000])

    def test_mix_num_written(self):
        text = "1.5, dreiviertel, eineinviertel Meilen"
        ants = list(get_amount_annotations(text))
        self.assertEqual(3, len(ants))

    def test_wrong_cases(self):
        self.assertSortedListEqual(list(get_amounts('...%')), [])

    def test_annotations(self):
        text = 'Sein Volumen beträgt 10 Liter und kostet dreißig Dollar'
        ants = list(get_amount_annotations(text))
        self.assertEqual(2, len(ants))
        self.assertEqual(10, ants[0].value)
        self.assertEqual((21, 24), ants[0].coords)

        self.assertEqual(30, ants[1].value)
        self.assertEqual(text.find(' dreißig'), ants[1].coords[0])

    def test_one_spelled_number(self):
        text = 'dreißig '
        ants = list(get_amount_annotations(text))
        self.assertEqual(1, len(ants))

    def test_apostrophe_delimiter(self):
        self.assertOneOK(15_000, "15'000 CHF")
        self.assertOneOK(Decimal('19_876.54'), "19'876.54 CHF")

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_amount_annotations,
            'lexnlp/typed_annotations/de/amount/amounts.txt',
            AmountAnnotation)
