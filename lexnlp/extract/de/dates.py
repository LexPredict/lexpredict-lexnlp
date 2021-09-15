__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

import os
from datetime import datetime
from typing import Generator, Optional

import joblib

from lexnlp.extract.all_locales.languages import Locale
from lexnlp.extract.common.annotations.date_annotation import DateAnnotation
from lexnlp.extract.de.date_model import DATE_MODEL_CHARS, DE_ALPHA_CHAR_SET

# Setup path
from lexnlp.extract.de.de_date_parser import DeDateParser

MODULE_PATH = os.path.dirname(os.path.abspath(__file__))

# Load model
MODEL_DATE = joblib.load(os.path.join(MODULE_PATH, "./date_model.pickle"))


parser = DeDateParser(DATE_MODEL_CHARS,
                      enable_classifier_check=True,
                      locale=Locale('de-DE'),
                      dateparser_settings={'PREFER_DAY_OF_MONTH': 'first',
                                           'STRICT_PARSING': False,
                                           'DATE_ORDER': 'DMY'},
                      classifier_model=MODEL_DATE,
                      alphabet_character_set=DE_ALPHA_CHAR_SET,
                      count_words=True,
                      feature_window=0)


def get_date_annotations(text: str,
                         strict: Optional[bool] = None,
                         locale: Optional[str] = '',
                         _base_date: Optional[datetime] = None,
                         _threshold: float = 0.50) -> Generator[DateAnnotation, None, None]:
    strict = strict if strict is not None else False
    yield from parser.get_date_annotations(text, Locale(locale), strict)


get_dates = parser.get_dates

get_date_list = parser.get_date_list
