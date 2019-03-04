"""
Date extraction for Spanish.
Dates parser based on dateparser package
"""
# pylint: disable=bare-except


import regex as re
from dateparser.data.date_translation_data.es import info

from lexnlp.extract.common.dates import DateParser


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
ES_MONTHS = sorted([y.lower() for k, v in info.items() if k in months for y in v],
                   key=lambda i: (-len(i), i))


class ESDateParser(DateParser):
    DATEPARSER_SETTINGS = {'PREFER_DAY_OF_MONTH': 'first', 'STRICT_PARSING': False}
    ENABLE_CLASSIFIER_CHECK = False
    SEQUENTIAL_DATES_RE = re.compile(
        r'(?P<text>(?P<day>\d{{1,2}}) de (?P<month>{es_months})(?:, | y | de (?P<year>\d{{4}})))'.format(
            es_months='|'.join(ES_MONTHS)), re.I | re.M)
    WEIRD_DATES_NORM = [
        (re.compile(r'(\d+º\s?de (?:{es_months})(?: de \d{{4}})?)'.format(
            es_months='|'.join(ES_MONTHS)), re.I | re.M),
         lambda i: re.sub(r'\s*º\s*', ' ', i))
    ]

    def get_extra_dates(self):
        dateparser_dates_dict = {i[0]: i for i in self.DATES}
        last_match_start = last_match_year = None
        dates_rev = reversed(list(self.SEQUENTIAL_DATES_RE.finditer(self.TEXT)))
        for match in dates_rev:
            capture = match.capturesdict()
            capture_text = ''.join(capture['text']).strip(',y ')
            match_start, match_end = match.span()
            if capture['year']:
                last_match_year = int(''.join(capture['year']))
                if capture_text not in dateparser_dates_dict:
                    a_date = self.get_dateparser_dates(capture_text)
                    if a_date:
                        a_date = a_date[0]
                        dateparser_dates_dict[a_date[0]] = a_date
            elif last_match_year and last_match_start is not None and last_match_start == match_end:
                if capture_text not in dateparser_dates_dict:
                    a_date = self.get_dateparser_dates(capture_text)
                    if a_date:
                        date_str, a_date = a_date[0]
                        a_date = a_date.replace(year=last_match_year)
                        dateparser_dates_dict[date_str] = (capture_text, a_date)
                else:
                    a_date = dateparser_dates_dict[capture_text][1].replace(year=last_match_year)
                    if a_date:
                        dateparser_dates_dict[capture_text] = (dateparser_dates_dict[capture_text][0], a_date)
            last_match_start = match_start

        dates = list(dateparser_dates_dict.values())

        for w_date_re, w_date_norm in self.WEIRD_DATES_NORM:
            w_dates = w_date_re.findall(self.TEXT)
            for w_date_str in w_dates:
                date_str = w_date_norm(w_date_str)
                date_res = self.get_dateparser_dates(date_str)
                if date_res:
                    dates.append((w_date_str, date_res[0][1]))

        self.DATES = dates


get_dates = ESDateParser().get_dates
get_date_list = ESDateParser().get_date_list
