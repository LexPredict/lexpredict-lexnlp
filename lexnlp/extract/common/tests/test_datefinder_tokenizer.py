__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from unittest import TestCase
# from datefinder import DateFinder as DateFinderOld
from lexnlp.extract.common.date_parsing.datefinder import DateFinder


class TestDateTokenizer(TestCase):
    def test_get_tokens(self):
        text = "At 1997, 20 FEB here, in"
        dtok = DateFinder()
        tokens = dtok.tokenize_string(text)
        self.assertEqual(11, len(tokens))
        self.assertEqual('delimiters', tokens[7][1])

    def test_get_date_time(self):
        text = "March 20, 2015 3:30 pm GMT "
        dtok = DateFinder()
        tokens = dtok.tokenize_string(text)
        merged = dtok.merge_tokens(tokens)
        self.assertEqual(1, len(merged))

    def test_merge_tokens(self):
        text = "At 1997, 20 FEB here, in"
        dtok = DateFinder()
        tokens = dtok.tokenize_string(text)
        merged = dtok.merge_tokens(tokens)
        self.assertEqual(1, len(merged))
        self.assertEqual('At 1997, 20 FEB ', merged[0].match_str)
        self.assertEqual((0, 16), merged[0].indices)
        self.assertEqual('At', merged[0].captures['extra_tokens'][0].strip())

    def test_get_date_strings(self):
        text = """
                2. Amendment to Interest Rate. Beginning on February 1, 1998, and
                        continuing until July 18, 2002, which is the fifth anniversary of the Loan
                        conversion date, interest shall be fixed at an annual rate of 7.38%, which rate
                        is equal to 200 basis points above the Bank's five-year ""Treasury Constant
                        Rate"" in effect on January 23, 1998. In accordance with the Agreement, the
                        interest rate shall be adjusted again on July 18, 2002.
                """
        dtok = DateFinder()
        dstrs = list(dtok.extract_date_strings(text, True))
        self.assertEqual(4, len(dstrs))
        self.assertEqual('until July 18, 2002', dstrs[1][0])
        self.assertEqual((118, 137), dstrs[1][1])
        groups = dstrs[1][2]
        self.assertEqual([], groups['time'])
        self.assertEqual('18', groups['digits'][0])
        self.assertEqual('2002', groups['digits'][1])

    # def test_compare_date_string(self):
    #     text = """
    #            In the event the real estate taxes levied or assessed against the land
    #            and building of which the premises are a part in future tax years are
    #            greater than the real estate taxes for the base tax year, the TENANT,
    #            shall pay within thirty (30) days after submission of the bill to TENANT for the increase in
    #            real estate taxes, as additional rent a proportionate share of such
    #            increases, which proportionate share shall be computed at 22.08% of the
    #            increase in taxes, but shall exclude any fine, penalty, or interest
    #            charge for late or non-payment of taxes by LANDLORD. The base tax year
    #            shall be July 1, 1994 to June 30, 1995.
    #            """
    #     dtok = DateFinder()
    #     tokens = dtok.tokenize_string(text)
    #     merged = dtok.merge_tokens(tokens)
    #
    #     pattern_start = """at 22.08# July 1, 1994 to June 30, 1995."""
    #     merged_start = '#'.join([m.match_str for m in merged]).strip()
    #     self.assertEqual(pattern_start, merged_start)
    #
    #     dstrs = list(dtok.extract_date_strings(text, strict=True))
    #     dold = DateFinderOld()
    #     ostrs = list(dold.extract_date_strings(text, strict=True))
    #
    #     # tokenizers has slightly different logic
    #     self.assertGreaterEqual(len(dstrs), len(ostrs))
