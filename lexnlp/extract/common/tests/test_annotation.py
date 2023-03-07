__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from datetime import date
from unittest import TestCase

from lexnlp.extract.common.annotations.trademark_annotation import TrademarkAnnotation
from lexnlp.extract.common.annotations.url_annotation import UrlAnnotation
from lexnlp.extract.common.annotations.ratio_annotation import RatioAnnotation
from lexnlp.extract.common.annotations.phone_annotation import PhoneAnnotation
from lexnlp.extract.common.annotations.ssn_annotation import SsnAnnotation
from lexnlp.extract.common.annotations.percent_annotation import PercentAnnotation
from lexnlp.extract.common.annotations.money_annotation import MoneyAnnotation
from lexnlp.extract.common.annotations.act_annotation import ActAnnotation
from lexnlp.extract.common.annotations.amount_annotation import AmountAnnotation
from lexnlp.extract.common.annotations.citation_annotation import CitationAnnotation
from lexnlp.extract.common.annotations.condition_annotation import ConditionAnnotation
from lexnlp.extract.common.annotations.constraint_annotation import ConstraintAnnotation
from lexnlp.extract.common.annotations.cusip_annotation import CusipAnnotation
from lexnlp.extract.common.annotations.date_annotation import DateAnnotation
from lexnlp.extract.common.annotations.court_annotation import CourtAnnotation
from lexnlp.extract.common.annotations.copyright_annotation import CopyrightAnnotation


class TestAnnotation(TestCase):

    def test_format_copyright_annotation(self):
        cp = CopyrightAnnotation(name='Siemens',
                                 coords=(0, 100),
                                 text='text text',
                                 locale='locale',
                                 company='Siemens',
                                 year_start=1996)
        s = cp.get_cite()  # '/copyright/Siemens/1996'
        self.assertGreater(s.find('copyright'), -1)
        self.assertGreater(s.find('Siemens'), -1)
        self.assertGreater(s.find('1996'), -1)

        cp.year_end = 2019
        cp.locale = 'en'
        s = cp.get_cite()  # '/en/copyright/Siemens/1996/2019'
        self.assertGreater(s.find('copyright'), -1)
        self.assertGreater(s.find('Siemens'), -1)
        self.assertGreater(s.find('1996'), -1)
        self.assertGreater(s.find('2019'), -1)

    def test_repr(self):
        ant = CourtAnnotation(name='GrossCourt',
                              coords=(1, 10), text='Court Gross',
                              locale='EN')
        s = ant.__repr__()
        self.assertGreater(len(s), 0)

    def test_act_annotation(self):
        ant = ActAnnotation(coords=(20, 92),
                            act_name='Some act',
                            section='p IV',
                            year=2021,
                            ambiguous=True,
                            text='Some act of 2021, p IV')

        s = ant.__repr__()
        self.assertGreater(len(s), 0)

        cite = ant.get_cite()
        self.assertEqual('/en/act/Some act/p IV/2021', cite)

        old_dic = ant.to_dictionary_legacy()
        self.assertEqual(20, old_dic['location_start'])
        self.assertEqual(92, old_dic['location_end'])
        self.assertEqual('Some act', old_dic['act_name'])
        self.assertEqual('p IV', old_dic['section'])
        self.assertEqual(str(2021), old_dic['year'])
        self.assertEqual(True, old_dic['ambiguous'])
        self.assertEqual('Some act of 2021, p IV', old_dic['value'])

        ant = ActAnnotation(coords=(20, 92),
                            act_name='Some act',
                            ambiguous=False,
                            text='Some act of 2021, p IV',
                            locale='pg')
        cite = ant.get_cite()
        self.assertEqual('/pg/act/Some act', cite)
        self.assertEqual('pg', ant.locale)

    def test_date_annotation(self):
        ant = DateAnnotation(coords=(2, 12),
                             date=date(2018, 1, 13),
                             score=0.5,
                             locale='pg')
        self.assertEqual('pg', ant.locale)
        s = ant.__repr__()
        self.assertGreater(len(s), 0)

        cite = ant.get_cite()
        self.assertEqual('/pg/date/2018-01-13', cite)

    def test_amount_annotation(self):
        ant = AmountAnnotation(coords=(2, 12),
                               value=2.3,
                               locale='pg')
        self.assertEqual('pg', ant.locale)
        s = ant.__repr__()
        self.assertGreater(len(s), 0)

        cite = ant.get_cite()
        self.assertEqual('/pg/amount/2.3', cite)

    def test_citation_annotation(self):
        ant = CitationAnnotation(coords=(2, 12),
                                 volume=1,
                                 year=1998,
                                 reporter='A. Husseini',
                                 reporter_full_name='Amin al-Husseini',
                                 page=14,
                                 page_range='14-15',
                                 source='Quran',
                                 court='sharia',
                                 locale='pg')
        self.assertEqual('pg', ant.locale)
        s = ant.__repr__()
        self.assertGreater(len(s), 0)

        cite = ant.get_cite()
        self.assertEqual('/pg/citation/Quran/1/1998/14-15/sharia/A. Husseini', cite)

    def test_condition_annotation(self):
        ant = ConditionAnnotation(coords=(1, 41),
                                  condition='in case of',
                                  pre='murder',
                                  post='dial "M"')
        self.assertEqual('en', ant.locale)
        s = ant.__repr__()
        self.assertGreater(len(s), 0)

        cite = ant.get_cite()
        self.assertEqual('/en/condition/in case of/murder/dial &quot;M&quot;', cite)

    def test_constraint_annotation(self):
        ant = ConstraintAnnotation(coords=(1, 41),
                                   constraint='when you are dead',
                                   post='never drive a car')
        self.assertEqual('en', ant.locale)
        s = ant.__repr__()
        self.assertGreater(len(s), 0)

        cite = ant.get_cite()
        self.assertEqual('/en/constraint/when you are dead/never drive a car', cite)

    def test_copyright_annotation(self):
        ant = CopyrightAnnotation(coords=(2, 20),
                                  year_start=1998,
                                  year_end=2001)
        cite = ant.get_cite()
        self.assertEqual('/en/copyright/1998/2001', cite)

    def test_cusip_annotation(self):
        ant = CusipAnnotation(coords=(2, 20),
                              code='SBN11',
                              tba='tba1',
                              ppn='ppn1',
                              internal=True,
                              checksum='0x0A')
        self.assertEqual('en', ant.locale)
        cite = ant.get_cite()
        self.assertEqual('/en/cusip/SBN11/ppn1', cite)

        ldic = ant.to_dictionary_legacy()
        self.assertEqual(True, ldic['internal'])
        self.assertEqual('SBN11', ldic['text'])

    def test_money_annotation(self):
        ant = MoneyAnnotation(coords=(2, 20),
                              amount=1001,
                              locale='de',
                              currency='JPY')
        self.assertEqual('de', ant.locale)
        cite = ant.get_cite()
        self.assertEqual('/de/money/1001/JPY', cite)

    def test_percent_annotation(self):
        ant = PercentAnnotation(coords=(2, 20),
                              amount=101,
                              sign='percento')
        self.assertEqual('en', ant.locale)
        cite = ant.get_cite()
        self.assertEqual('/en/percent/101/percento', cite)

    def test_ssn_annotation(self):
        ant = SsnAnnotation(coords=(2, 20),
                            number='1234-4321-1234')
        self.assertEqual('en', ant.locale)
        cite = ant.get_cite()
        self.assertEqual('/en/ssn/1234-4321-1234', cite)

    def test_phone_annotation(self):
        ant = PhoneAnnotation(coords=(2, 20),
                              phone='(4) 4321-33-22-1')
        self.assertEqual('en', ant.locale)
        cite = ant.get_cite()
        self.assertEqual('/en/phone/(4) 4321-33-22-1', cite)

    def test_ratio_annotation(self):
        ant = RatioAnnotation(coords=(2, 20),
                              left=11,
                              right=2,
                              ratio=11 / 2.0)
        self.assertEqual('en', ant.locale)
        cite = ant.get_cite()
        self.assertEqual('/en/ratio/11/2', cite)

    def test_url_annotation(self):
        ant = UrlAnnotation(coords=(2, 20),
                            url='https://en.wikipedia.org/wiki/Social_Security_number')
        self.assertEqual('en', ant.locale)
        cite = ant.get_cite()
        self.assertEqual('/en/url/https://en.wikipedia.org/wiki/Social_Security_number', cite)

    def test_trademark_annotation(self):
        ant = TrademarkAnnotation(coords=(2, 20),
                                  trademark='CZ')
        self.assertEqual('en', ant.locale)
        cite = ant.get_cite()
        self.assertEqual('/en/trademark/CZ', cite)
