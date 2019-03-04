"""
Date extraction
Dates parser based on dateparser package
"""
# pylint: disable=bare-except,broad-except,unused-argument

import re
import pandas as pd
import string

from dateparser.search import search_dates
from lexnlp.extract.en.date_model import MODEL_DATE, get_date_features


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DateParser(object):
    """
    Dates parser based on dateparser package
    """
    ENABLE_CLASSIFIER_CHECK = True
    CLASSIFIER_MODEL = MODEL_DATE
    CLASSIFIER_THRESHOLD = 0.5
    BAD_FULL_RE = re.compile(r'\d+\W?|(?:\d+\.? )?die|so|\d+ und \d+|die in einem', re.I)
    BAD_PARTIAL_RE = re.compile('[%s]' % re.escape(re.sub('[.,-:]', '', string.punctuation)))
    DATEPARSER_SETTINGS = {'PREFER_DAY_OF_MONTH': 'first', 'STRICT_PARSING': False}

    def __init__(self, text=None, language='en', dateparser_settings=None,
                 enable_classifier_check=None, classifier_model=None, classifier_threshold=None):
        """
        :param language: str - two-letters language definition
        :param enable_classifier_check: bool - enable date check using classifier model
        :param classifier_model: obj - classifier itself
        :param classifier_threshold: float 0<x<1 - min value to predict date
        :param dateparser_settings: dict - settings for dateparser
        """
        self.LANGUAGE = language
        self.TEXT = text
        self.DATES = []
        self.ENABLE_CLASSIFIER_CHECK = enable_classifier_check \
            if enable_classifier_check is not None else self.ENABLE_CLASSIFIER_CHECK
        self.CLASSIFIER_MODEL = classifier_model or self.CLASSIFIER_MODEL
        self.CLASSIFIER_THRESHOLD = classifier_threshold or self.CLASSIFIER_THRESHOLD
        self.DATEPARSER_SETTINGS = dateparser_settings or self.DATEPARSER_SETTINGS

    def get_dateparser_dates(self, text=None):
        """
        Extract possible dates with dateparser
        """
        text = text or self.TEXT
        # INFO: 'DATE_ORDER': 'DMY' prevents parsing date like 2004-12-13T00:00:00Z,
        #  use SKIP_TOKENS setting if needed along with DATE_ORDER
        return search_dates(text, languages=[self.LANGUAGE], settings=self.DATEPARSER_SETTINGS) or []

    def get_extra_dates(self):
        """
        Add custom search logic; use self.TEXT, self.LANGUAGE, self.DATES; update self.DATES
        :return: None
        """
        # self.DATES += (custom logic)
        pass

    def passed_general_check(self, date_str, date):
        """
        Apply custom checks like for unwanted symbols in a date
        """
        return not (self.BAD_FULL_RE.fullmatch(date_str) or self.BAD_PARTIAL_RE.search(date_str))

    def passed_classifier_check(self, location_start, location_end):
        """
        Use pre-trained classifier model to predict whether a date has right format
        Should be pluggable as it takes 90% parsing time
        """
        row_df = pd.DataFrame.from_records(
            [get_date_features(self.TEXT, location_start, location_end)])
        date_score = self.CLASSIFIER_MODEL.predict_proba(
            row_df.loc[:, self.CLASSIFIER_MODEL.columns])
        return date_score[0, 1] > self.CLASSIFIER_THRESHOLD

    def get_dates(self, text=None, language=None):
        self.TEXT = text or self.TEXT
        self.LANGUAGE = language or self.LANGUAGE

        if not self.TEXT or not self.LANGUAGE:
            raise RuntimeError('Define text and language.')

        # First try dateparser searcher
        try:
            self.DATES = self.get_dateparser_dates() or []
        except Exception as e:
            # TODO: add logging
            print(str(e))

        # Next try custom search logic
        self.get_extra_dates()

        positions = []
        for date_str, date in sorted(self.DATES, key=lambda i: -len(i[0])):

            # if possible date has weird format or unwanted symbols
            if not self.passed_general_check(date_str, date):
                continue

            for match in re.finditer(re.escape(date_str), self.TEXT):
                location_start, location_end = match.span()

                # skip overlapping entities
                if any([1 for i, j in positions if location_start>=i and location_end<=j]):
                    continue
                positions.append(match.span())

                # filter out possible dates using classifier
                if self.ENABLE_CLASSIFIER_CHECK and \
                        not self.passed_classifier_check(location_start, location_end):
                    continue

                yield {'location_start': location_start,
                       'location_end': location_end,
                       'value': date,
                       'source': self.TEXT[location_start:location_end]}

    def get_date_list(self, *args, **kwargs):
        return list(self.get_dates(*args, **kwargs))


get_dates = DateParser().get_dates
get_date_list = DateParser().get_date_list
