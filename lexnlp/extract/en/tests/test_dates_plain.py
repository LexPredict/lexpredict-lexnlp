__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import datetime
from unittest import TestCase

from lexnlp.extract.common.annotations.date_annotation import DateAnnotation
from lexnlp.extract.en.dates import get_raw_date_list, get_dates_list, get_date_annotations
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


class TestDatesPlain(TestCase):

    def test_dates(self):
        text = """
        2. Amendment to Interest Rate. Beginning on February 1, 1998, and
                continuing until July 18, 2002, which is the fifth anniversary of the Loan
                conversion date, interest shall be fixed at an annual rate of 7.38%, which rate
                is equal to 200 basis points above the Bank's five-year ""Treasury Constant
                Rate"" in effect on January 23, 1998. In accordance with the Agreement, the
                interest rate shall be adjusted again on July 18, 2002.
        """
        dates = get_raw_date_list(text)
        self.assertEqual(4, len(dates))
        self.assertEqual(datetime.date(1998, 2, 1), dates[0])
        self.assertEqual(datetime.date(2002, 7, 18), dates[1])
        self.assertEqual(datetime.date(1998, 1, 23), dates[2])
        self.assertEqual(datetime.date(2002, 7, 18), dates[3])

    def test_dates_times(self):
        text = "From 12:01 a.m. on March 1, 1999 (the 'Commencement Date') through " + \
               "1l:59 p.m. on November 30, 2002 (the 'Expiration Date')"
        dates = get_raw_date_list(text)

        self.assertEqual(2, len(dates))
        self.assertEqual(datetime.datetime(1999, 3, 1, 0, 1), dates[0])
        self.assertEqual(datetime.date(2002, 11, 30), dates[1])

    def test_moar_dates(self):
        text = """
        2. Amendment to Interest Rate. Beginning on February 1, 1998, and
        continuing until July 18, 2002, which is the fifth anniversary of the Loan
        conversion date, interest shall be fixed at an annual rate of 7.38%, which rate
        is equal to 200 basis points above the Bank's five-year "Treasury Constant
        Rate" in effect on January 23, 1998. In accordance with the Agreement, the
        interest rate shall be adjusted again on July 18, 2002.
        """

        dates = get_dates_list(text)
        self.assertEqual(4, len(dates))

    def test_no_dates(self):
        text = """
        18.1 Methods of Application 1-57 18.2 Issue of Certificate of payment 1-57 18.3
                           Corrections to Certificates of Payment 1-58 18.4 Payment 1-58 18.5 Delayed Payment 1-58
                           18.6 Remedies on Failure to Certify or Make Payment 1-58 18.7 Application for Final
                           Certificate of Payment 1-59 18.8 Issue of final Certificate of Payment 1-59 18.9 Final
                           Certificate of Payment conclusive 1-60 18.10 Advance Payment 1-60 18.11 Advance Payment
                           Guarantee 1-60 18.12 Terms of Payment 1-60 18.13 Retention 1-61
        """
        get_raw_date_list(text)
        # self.assertEqual(len(dates), 1)

    def test_more_more_dates(self):
        text = """
        In the event the real estate taxes levied or assessed against the land
                       and building of which the premises are a part in future tax years are
                       greater than the real estate taxes for the base tax year, the TENANT,
                       shall pay within thirty (30) days after submission of the bill to TENANT for the increase in
                       real estate taxes, as additional rent a proportionate share of such
                       increases, which proportionate share shall be computed at 22.08% of the
                       increase in taxes, but shall exclude any fine, penalty, or interest
                       charge for late or non-payment of taxes by LANDLORD. The base tax year
                       shall be July 1, 1994 to June 30, 1995.
        """
        dates = get_dates_list(text)
        self.assertEqual(2, len(dates))

    def test_two_ranges(self):
        text = """
        be July 1, 1994 to June 30, 1995 through 10/07/1998
        """
        dates = get_dates_list(text)
        self.assertEqual(len(dates), 3)

    def test_two_dates_strict(self):
        text = """
            This monthly maintenance and support arrangement will have an initial term of six (6)
            months. The arrangement will then automatically renew for an additional twelve (12) months
            at the above rates and conditions unless written notification to US/INTELICOM of Licensee's
            intent to cancel the arrangement is received no later than September 1, 1998. Unless
            Licensee elects to cancel this arrangement at the end of the first six months, the "initial
            term" of the arrangement will be through September 30, 1999.
        """
        dates = get_dates_list(text)
        self.assertEqual(2, len(dates))

    def test_one_date_this(self):
        text = """made this November 16, 2009. This is a paragraph which has multiple sentences."""
        dates = get_dates_list(text)
        self.assertEqual(1, len(dates))

    def test_august(self):
        text = """Commencement Date: August 1, 2013."""
        dates = get_dates_list(text)
        self.assertEqual(1, len(dates))
        self.assertEqual(8, dates[0].month)

    def test_date_first_aug(self):
        dates = list(get_dates_list("second of August 2014"))
        self.assertEqual(1, len(dates))

        dates = get_dates_list("2nd of August 2014")
        self.assertEqual(1, len(dates))

    def test_fp(self):
        text = """ this Section 13.2 may exercise all"""
        dates = list(get_dates_list(text, strict=True))
        self.assertEqual(0, len(dates))

    def test_section(self):
        text = "Section 7.7.10 may be made"
        dates = list(get_dates_list(text, strict=True))
        self.assertEqual(0, len(dates))

    def test_another_may(self):
        text = "Sections 12.1, 12.2, 12.3, 12.4, 12.6, 12.7 and 12.12\n" + \
               "may be amended only"
        dates = list(get_dates_list(text, strict=True))
        self.assertEqual(0, len(dates))

    def test_should_be_fixed(self):
        text = """
        This Amendment to the Employment Agreement (the "Amendment") is made as of
        the 20th day of May, 2003 between Cromcor Inc. (the "Company") and [Executive's
        Name - See Schedule A attached hereto] (the "Executive").
        """
        dates = list(get_dates_list(text, strict=True))
        self.assertEqual(0, len(dates))

    def test_is_it_a_date(self):
        """
        Somehow "29MAY19 1350" produces 1350-01-01 that doesn't go through validation
        """
        text = "NOT RCVD BY RJ BY 29MAY19 1350 DOH LT REF"
        dates = list(get_dates_list(text, strict=True))
        self.assertEqual(1, len(dates))
        self.assertEqual(datetime.datetime(2019, 5, 29, 13, 50, 0), dates[0])

    def test_date_en_us(self):
        text = 'Commencement Date: 09/12/2022.'
        dates = get_dates_list(text)
        self.assertEqual(1, len(dates))
        self.assertEqual(9, dates[0].month)

    def test_date_en_gb(self):
        text = 'Commencement Date: 09/12/2022.'
        dates = get_dates_list(text, locale='en-GB')
        self.assertEqual(1, len(dates))
        self.assertEqual(12, dates[0].month)

    def test_date_with_abbreviation(self):
        text = "'“Obligation No. 1” means Direct Note Obligation No. 1 dated October 27, 2011, " \
               "issued to the Authority under the First Supplemental Master Indenture to secure " \
               "the Series 2000 COPs.'"
        dates = get_dates_list(text)
        self.assertEqual(1, len(dates))
        self.assertEqual(datetime.date(2011, 10, 27), dates[0])

    def test_en_dates(self):
        text = "Some date like February 26, 2018 and this one 10-11-2017"
        extracted_dates = list(get_date_annotations(text=text, locale='en'))
        for ant in extracted_dates:
            ant.text = text[ant.coords[0]: ant.coords[1]]
        extracted_dates.sort(key=lambda k: k.coords[0])

        self.assertEqual((15, 32), extracted_dates[0].coords)
        self.assertEqual(datetime.date(2018, 2, 26), extracted_dates[0].date)
        self.assertEqual('February 26, 2018', extracted_dates[0].text.strip())

        self.assertEqual((46, 56), extracted_dates[1].coords)
        self.assertEqual(datetime.date(2017, 10, 11), extracted_dates[1].date)
        self.assertEqual('10-11-2017', extracted_dates[1].text.strip())

    def test_should_marella(self):
        text = """
        A broker’s fee for the professional services of 6% is due from the SELLER to Nahum Omeler of Romy Realty, 
        LLC, the Broker herein, to be divided with Buyer’s broker, Maureen Marella-Devlin of 
        Century 21 Marella Realty (4% to Romy Realty, LLC and 2% to Century 21 Marella Realty).
        """
        dates = list(get_dates_list(text, strict=False))
        self.assertEqual(0, len(dates))

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_date_annotations,
            'lexnlp/typed_annotations/en/date/dates.txt',
            DateAnnotation)
