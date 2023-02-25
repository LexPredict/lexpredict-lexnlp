"""
Date extraction
Dates parser based on dateparser package
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# pylint: disable=bare-except,broad-except,unused-argument
import datetime
import re
from importlib import import_module

import string

from dateparser.search import search_dates
from typing import Generator, Any, Dict, Optional, Tuple, List, Set

from lexnlp.extract.all_locales.languages import Locale
from lexnlp.extract.common.annotations.date_annotation import DateAnnotation
from lexnlp.extract.common.dates_classifier_model import get_date_features


class LocaleInfoImport:
    def __init__(self, locale):
        try:
            module = import_module('dateparser.data.date_translation_data.' + locale.language)
            data_dict = getattr(module, 'info')
            if data_dict.get('locale_specific', None) and locale.get_locale() in data_dict['locale_specific']:
                self.date_order = data_dict['locale_specific'][locale.get_locale()]['date_order']
            else:
                self.date_order = data_dict['date_order']
        except ModuleNotFoundError:
            self.date_order = "MDY"


class DateParser:
    """
    Dates parser based on dateparser package
    """
    BAD_FULL_RE = re.compile(r'\d+\W?|(?:\d+\.? )?die|so|\d+ und \d+|die in einem', re.I)
    BAD_PARTIAL_RE = re.compile('[%s]' % re.escape(re.sub('[.,-:]', '', string.punctuation)))
    DEFAULT_DATEPARSER_SETTINGS = {'PREFER_DAY_OF_MONTH': 'first', 'STRICT_PARSING': False}

    def __init__(self,
                 characters: List[str],
                 text: Optional[str] = None,
                 locale: Locale = Locale('en-US'),
                 dateparser_settings: Optional[Dict[str, Any]] = None,
                 enable_classifier_check: bool = True,
                 classifier_model: Optional[Any] = None,
                 classifier_threshold: float = 0.5,
                 alphabet_character_set: Optional[Set[str]] = None,
                 count_words=False,
                 feature_window=5):
        """
        :param locale: locale object with language code and locale code
        :param enable_classifier_check: bool - enable date check using classifier model
        :param classifier_model: obj - classifier itself
        :param classifier_threshold: float 0<x<1 - min value to predict date
        :param dateparser_settings: dict - settings for dateparser
        """
        self.characters = characters
        self.count_words = count_words
        self.alphabet_character_set = alphabet_character_set
        self.locale = locale
        self.text = text
        self.dates = []
        self.enable_classifier_check = enable_classifier_check
        self.classifier_model = classifier_model
        self.classifier_threshold = classifier_threshold
        self.dateparser_settings = dateparser_settings or self.DEFAULT_DATEPARSER_SETTINGS
        self.feature_window = feature_window

    def get_dateparser_dates(self,
                             text: Optional[str],
                             strict: bool) -> List[Tuple[str, datetime.datetime]]:
        """
        Extract possible dates with dateparser
        """
        text = text or self.text
        # INFO: 'DATE_ORDER': 'DMY' prevents parsing date like 2004-12-13T00:00:00Z,
        #  use SKIP_TOKENS setting if needed along with DATE_ORDER
        old_strict_mode = self.dateparser_settings['STRICT_PARSING']
        self.dateparser_settings['STRICT_PARSING'] = strict
        old_date_order = self.dateparser_settings['PREFER_DAY_OF_MONTH']
        self.dateparser_settings['DATE_ORDER'] = LocaleInfoImport(self.locale).date_order
        dates = search_dates(text, languages=[self.locale.language], settings=self.dateparser_settings)
        self.dateparser_settings['STRICT_PARSING'] = old_strict_mode
        self.dateparser_settings['DATE_ORDER'] = old_date_order
        return dates or []

    def get_extra_dates(self, strict: bool):
        """
        Add custom search logic; use self.TEXT, self.LANGUAGE, self.DATES; update self.DATES
        :return: None
        """
        # self.DATES += (custom logic)

    def passed_general_check(self, date_str: str, _date):
        """
        Apply custom checks like for unwanted symbols in a date
        """
        return not (self.BAD_FULL_RE.fullmatch(date_str) or self.BAD_PARTIAL_RE.search(date_str))

    def passed_classifier_check(self, location_start, location_end):
        """
        Use pre-trained classifier model to predict whether a date has right format
        Should be pluggable as it takes 90% parsing time
        """
        features = [get_date_features(self.text,
                                      location_start,
                                      location_end, self.characters,
                                      self.alphabet_character_set,
                                      count_words=self.count_words,
                                      window=self.feature_window)][0]
        # rearrange the features to self.classifier_model.columns order
        feature_list = len(features) * [0.0]
        for i, col in enumerate(self.classifier_model.columns):
            feature_list[i] = features[col]
        date_score = self.classifier_model.predict_proba([feature_list])
        return date_score[0, 1] > self.classifier_threshold

    def get_dates(self,
                  text: Optional[str] = None,
                  locale: Optional[Locale] = None) \
            -> Generator[Dict[str, Any], None, None]:
        strict = self.dateparser_settings.get('STRICT_PARSING',
                                              self.DEFAULT_DATEPARSER_SETTINGS.get('STRICT_PARSING', False))
        for ant in self.get_date_annotations(text, locale, strict=strict):
            yield {'location_start': ant.coords[0],
                   'location_end': ant.coords[1],
                   'value': ant.date,
                   'source': ant.text}

    def get_date_annotations(self,
                             text: str = None,
                             locale: Optional[Locale] = None,
                             strict: bool = True) -> \
            Generator[DateAnnotation, None, None]:
        self.text = text.replace('\n', ' ') or self.text
        self.locale.language = (locale.language if locale else "") or self.locale.language

        if not self.text or not self.locale.language:
            raise RuntimeError('Define text and language.')

        # First try dateparser searcher
        try:
            self.dates = self.get_dateparser_dates(text, strict)
        except Exception as e:
            # TODO: add logging
            print(str(e))

        # Next try custom search logic
        self.get_extra_dates(strict)

        positions = []
        for date_str, date in sorted(self.dates, key=lambda i: -len(i[0])):

            # if possible date has weird format or unwanted symbols
            if not self.passed_general_check(date_str, date):
                continue

            for match in re.finditer(re.escape(date_str), self.text):
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
                                     text=self.text[location_start:location_end],
                                     locale=self.locale.language)
                yield ant

    def get_date_list(self, text, locale):
        return list(self.get_dates(text, locale))

    def get_date_annotation_list(
        self,
        text: str = None,
        locale: Optional[Locale] = None,
        strict: bool = True,
    ) -> List[DateAnnotation]:
        return list(self.get_date_annotations(text, locale, strict))
