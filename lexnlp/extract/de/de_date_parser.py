__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import datetime
import regex as re
from typing import List, Optional, Generator

import zahlwort2num as w2n

from lexnlp.extract.all_locales.languages import Locale
from lexnlp.extract.common.annotations.date_annotation import DateAnnotation
from lexnlp.extract.common.dates import DateParser
from lexnlp.extract.common.dates_classifier_model import split_date_words, REG_NUMBER
from lexnlp.extract.de.date_model import MONTH_NAMES, DE_ALPHA_CHAR_SET


MONTH_NAMES_LOWER = set([m.lower() for m in MONTH_NAMES])
MONTH_NAMES_SHORT = set([m[:3].lower() for m in MONTH_NAMES])

CUSTOM_DATES_SEPARATOR = re.compile(r'(?<=[\W|\d])\sund\s')


class DatePart:
    def __init__(self,
                 text: str,
                 category: str,
                 num_value: int = 0):
        self.text = text
        self.category = category
        self.num_value = num_value
        self.is_cap = len(text) > 1 and text[0].lower() != text[0] and text[1].lower() == text[1]

    def __str__(self):
        return f'{self.text} [{self.category}]'

    def __repr__(self):
        return self.__str__()


class DeDateParser(DateParser):

    def passed_general_check(self,
                             date_str: str,
                             date: datetime.date) -> bool:
        if not super().passed_general_check(date_str, date):
            return False
        parts = self.get_word_parts(date_str)
        if len(parts) < 2:
            return False

        number_values: List[int] = []
        numbers, possible_months, possible_days, possible_years = 0, 0, 0, 0
        for p in parts:
            if p.category == 'number':
                number_values.append(p.num_value)
            if 0 < p.num_value < 13:
                possible_months += 1
            if 0 < p.num_value < 31:
                possible_days += 1
            if p.num_value > 0:
                possible_years += 1

            if p.category == 'month':
                possible_months += 1
                numbers += 1
            if p.category == 'number':
                numbers += 1
        if possible_months == 0:
            return False  # no date can be written w/o month
        if numbers < 2:
            return False
        # compare numbers found in the string (number_values) to
        # e.g. "24 Stunden 5": number_values = [24, 5], date = (2006, 11, 5)
        # only one of the two number values are in the date components (5)
        date_numbers = {date.year, date.month, date.day}
        hits, misses = 0, 0
        for n in number_values:
            if n in date_numbers:
                hits += 1
            else:
                misses += 1
        if misses > 0 and misses >= hits:
            return False
        return True

    def get_word_parts(self, date_str: str) -> List[DatePart]:
        parts: List[DatePart] = []
        for wrd in split_date_words(date_str):
            if not wrd:
                continue
            # is it a number of several digits?
            numbers = [int(n.group(0)) for n in REG_NUMBER.finditer(wrd)]
            if numbers:
                parts.append(DatePart(wrd, 'number', numbers[0]))
                continue

            # is it a month name?
            month_nm = wrd.lower()
            if month_nm in MONTH_NAMES_LOWER or month_nm in MONTH_NAMES_SHORT:
                parts.append(DatePart(wrd, 'month'))
                continue

            # is it a numeral?
            try:
                num_or_str = w2n.convert(wrd)
                if isinstance(num_or_str, str):
                    num_or_str = int(num_or_str.strip(' .'))
                if num_or_str < 0:
                    continue
                parts.append(DatePart(wrd, 'number', num_or_str))
                continue
            # pylint:disable=bare-except
            except:
                pass

            # is it a capitalized string?
            if wrd[0] not in DE_ALPHA_CHAR_SET:
                continue
            parts.append(DatePart(wrd, ''))
        return parts

    def get_date_annotations(self,
                             text: str = None,
                             locale: Optional[Locale] = None,
                             strict: bool = True) -> \
            Generator[DateAnnotation, None, None]:
        self.text = text.replace('\n', ' ') or self.text
        self.text = re.sub(CUSTOM_DATES_SEPARATOR, '\n', self.text)
        text_parts = self.text.split('\n')
        for text_part in text_parts:
            self.locale.language = (locale.language if locale else "") or self.locale.language

            if not text_part or not self.locale.language:
                raise RuntimeError('Define text and language.')

            # First try dateparser searcher
            try:
                self.dates = self.get_dateparser_dates(text_part, strict)
            except Exception as e:
                print(str(e))

            # Next try custom search logic
            self.get_extra_dates(strict)

            positions = []
            for date_str, date in sorted(self.dates, key=lambda i: -len(i[0])):

                # if possible date has weird format or unwanted symbols
                if not self.passed_general_check(date_str, date):
                    continue

                for match in re.finditer(re.escape(date_str), text_part):
                    location_start, location_end = match.span()

                    # skip overlapping entities
                    if any(1 for i, j in positions if location_start >= i and location_end <= j):
                        continue
                    positions.append(match.span())

                    # filter out possible dates using classifier
                    if self.enable_classifier_check and \
                            not self.passed_classifier_check(location_start, location_end):
                        continue

                    ant = DateAnnotation(coords=(location_start, location_end),
                                         date=date,
                                         text=text_part[location_start:location_end],
                                         locale=self.locale.language)
                    yield ant
