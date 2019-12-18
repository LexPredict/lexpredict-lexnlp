import codecs
import datetime
import os
import time
from unittest import TestCase
from lexnlp.extract.common.date_parsing.datefinder import DateFinder

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestDateFinder(TestCase):
    def test_parse_str(self):
        text = """
        ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 -                     569                -                     15                  -                     -                     -                     -                     -                     -                     -                     -                     -                     +
 1,195             1,339             3,019             1,820             13,831
        """
        base_date = datetime.datetime.now().replace(
            day=1, month=1, hour=0, minute=0, second=0, microsecond=0)

        # Find potential dates
        date_finder = DateFinder(base_date=base_date)
        possible_dates = [(date_string, index, date_props) for date_string, index, date_props in
                          date_finder.extract_date_strings(text, strict=False)]
        self.assertGreater(len(possible_dates), 0)

    def test_parse_time(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = dir_path + '/../../../../test_data/long_parsed_text.txt'
        with codecs.open(file_path, 'r', encoding='utf-8') as fr:
            text = fr.read()

        base_date = datetime.datetime.now().replace(
            day=1, month=1, hour=0, minute=0, second=0, microsecond=0)
        date_finder = DateFinder(base_date=base_date)
        t1 = time.time()
        _ = [(date_string, index, date_props) for date_string, index, date_props in
                          date_finder.extract_date_strings(text, strict=False)]
        d1 = time.time() - t1
        self.assertLess(d1, 15)
