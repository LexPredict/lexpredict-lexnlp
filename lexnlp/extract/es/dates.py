"""
Date extraction for Spanish.
Dates parser based on dateparser package
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# pylint: disable=bare-except
import string
from datetime import datetime
from typing import Optional, Dict, Any, Generator
import regex as re

# noinspection PyUnresolvedReferences
from dateparser.data.date_translation_data.es import info

from lexnlp.extract.all_locales.languages import Locale
from lexnlp.extract.common.annotations.date_annotation import DateAnnotation
from lexnlp.extract.common.dates import DateParser


months = ('january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december')
ES_MONTHS = sorted([y.lower() for k, v in info.items() if k in months for y in v],
                   key=lambda i: (-len(i), i))

ES_ALPHABET = ''
DATE_MODEL_CHARS = []
DATE_MODEL_CHARS.extend(ES_ALPHABET + string.ascii_letters)
DATE_MODEL_CHARS.extend(string.digits)
DATE_MODEL_CHARS.extend(["-", "/", " ", "%", "#", "$"])


class ESDateParser(DateParser):
    DEFAULT_DATEPARSER_SETTINGS = {'PREFER_DAY_OF_MONTH': 'first', 'STRICT_PARSING': False, 'DATE_ORDER': 'DMY'}
    SEQUENTIAL_DATES_RE = re.compile(
        r'(?P<text>(?P<day>\d{{1,2}})\s+de\s+(?P<month>{es_months})(?:,\s+|\s+y\s+|\s+de\s+(?P<year>\d{{4}})))'.format(
            es_months='|'.join(ES_MONTHS)), re.I | re.M)
    WEIRD_DATES_NORM = [
        (re.compile(r'(\d+º\s?de (?:{es_months})(?: de \d{{4}})?)'.format(
            es_months='|'.join(ES_MONTHS)), re.I | re.M),
         lambda i: re.sub(r'\s*º\s*', ' ', i))
    ]

    def __init__(self,
                 text: Optional[str] = None,
                 locale: Locale = Locale('en-US'),
                 dateparser_settings: Optional[Dict[str, Any]] = None,
                 enable_classifier_check: bool = False,
                 classifier_model: Optional[Any] = None,
                 classifier_threshold: float = 0.5):
        super().__init__(DATE_MODEL_CHARS, text, locale, dateparser_settings,
                         enable_classifier_check, classifier_model, classifier_threshold)

    def get_extra_dates(self, strict: bool):
        sequential_matches = list(self.SEQUENTIAL_DATES_RE.finditer(self.text))
        sequential_spans = [match.span() for match in sequential_matches]
        sequential_texts = {
            re.sub(r'\s+', ' ', ''.join(match.capturesdict()['text']).strip(',y '))
            for match in sequential_matches
        }

        # dateparser may treat the leading day from the next item in a
        # coordinated sequence as a two-digit year.  For example,
        # ``28 de abril y 17 de noviembre de 1995`` has been returned as the
        # spurious ``28 de abril y 17 de`` -> 2017-04-28.  The explicit
        # Spanish sequence parser below owns these spans, so discard only
        # non-canonical dateparser candidates that overlap them.
        dateparser_dates_dict = {}
        for date_item in self.dates:
            date_text = date_item[0]
            overlaps_sequence = any(
                candidate_start < sequence_end
                and candidate_end > sequence_start
                for candidate in self._find_date_matches(date_text, self.text)
                for candidate_start, candidate_end in [candidate.span()]
                for sequence_start, sequence_end in sequential_spans
            )
            if overlaps_sequence and re.sub(r'\s+', ' ', date_text) not in sequential_texts:
                continue
            dateparser_dates_dict[date_text] = date_item

        last_match_start = last_match_year = None
        dates_rev = reversed(sequential_matches)
        for match in dates_rev:
            capture = match.capturesdict()
            capture_text = ''.join(capture['text']).strip(',y ')
            match_start, match_end = match.span()
            if capture['year']:
                last_match_year = int(''.join(capture['year']))
                if capture_text not in dateparser_dates_dict:
                    a_date = self.get_dateparser_dates(capture_text, strict)
                    if a_date:
                        a_date = a_date[0]
                        dateparser_dates_dict[a_date[0]] = a_date
            elif last_match_year and last_match_start is not None and last_match_start == match_end:
                if capture_text not in dateparser_dates_dict:
                    keys_to_replace = [
                        key
                        for key in dateparser_dates_dict
                        if key.startswith(capture_text)
                    ]
                    for key in keys_to_replace:
                        dateparser_dates_dict.pop(key)
                    a_date = self.get_dateparser_dates(capture_text, strict)
                    if a_date:
                        _, a_date = a_date[0]
                        a_date = a_date.replace(year=last_match_year)
                        dateparser_dates_dict[capture_text] = (capture_text, a_date)
                else:
                    a_date = dateparser_dates_dict[capture_text][1].replace(year=last_match_year)
                    if a_date:
                        dateparser_dates_dict[capture_text] = (capture_text, a_date)
            last_match_start = match_start

        dates = list(dateparser_dates_dict.values())

        for w_date_re, w_date_norm in self.WEIRD_DATES_NORM:
            w_dates = w_date_re.findall(self.text)
            for w_date_str in w_dates:
                date_str = w_date_norm(w_date_str)
                date_res = self.get_dateparser_dates(date_str, strict)
                if date_res:
                    dates.append((w_date_str, date_res[0][1]))

        self.dates = dates


def _coerce_locale(locale: Optional[Locale]) -> Locale:
    if locale is None:
        return Locale('es-ES')
    if isinstance(locale, Locale):
        return Locale(locale.get_locale())
    return Locale(locale)


def _build_parser(
    locale: Optional[Locale] = None,
    *,
    base_date: Optional[datetime] = None,
    threshold: float = 0.5,
) -> ESDateParser:
    settings = {
        'PREFER_DAY_OF_MONTH': 'first',
        'STRICT_PARSING': False,
        'DATE_ORDER': 'DMY',
    }
    if base_date is not None:
        settings['RELATIVE_BASE'] = base_date
    return ESDateParser(
        enable_classifier_check=False,
        locale=_coerce_locale(locale),
        dateparser_settings=settings,
        classifier_threshold=threshold,
    )


# Retained for compatibility with callers which inspect the configured parser.
parser = _build_parser()


def get_dates(
    text: str = None,
    locale: Optional[Locale] = None,
) -> Generator[Dict[str, Any], None, None]:
    locale_obj = _coerce_locale(locale)
    yield from _build_parser(locale_obj).get_dates(text=text, locale=locale_obj)


def get_date_list(
    text: str = None,
    locale: Optional[Locale] = None,
):
    return list(get_dates(text=text, locale=locale))


def get_date_annotations(
    text: str = None,
    locale: Optional[Locale] = None,
    strict: bool = True,
    base_date: Optional[datetime] = None,
    threshold: float = 0.5,
) -> Generator[DateAnnotation, None, None]:
    """Extract Spanish dates, using ``base_date`` for incomplete dates.

    ``threshold`` is accepted for all-locale API compatibility; the Spanish
    parser does not enable a classifier check.
    """
    locale_obj = _coerce_locale(locale)
    yield from _build_parser(
        locale_obj, base_date=base_date, threshold=threshold,
    ).get_date_annotations(
        text=text,
        locale=locale_obj,
        strict=strict,
    )


def get_date_annotation_list(
    text: str = None,
    locale: Optional[Locale] = None,
    strict: bool = True,
    base_date: Optional[datetime] = None,
    threshold: float = 0.5,
):
    return list(
        get_date_annotations(
            text=text,
            locale=locale,
            strict=strict,
            base_date=base_date,
            threshold=threshold,
        )
    )
