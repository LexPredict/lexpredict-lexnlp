__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import os
from datetime import datetime
from typing import Generator, List, Optional

from lexnlp.extract.all_locales.languages import Locale
from lexnlp.extract.common.annotations.date_annotation import DateAnnotation
from lexnlp.extract.de.date_model import DATE_MODEL_CHARS, DE_ALPHA_CHAR_SET
from lexnlp.utils.unpickler import load_joblib_model

# Setup path
from lexnlp.extract.de.de_date_parser import DeDateParser


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))

# Load model
MODEL_DATE = load_joblib_model(os.path.join(MODULE_PATH, "./date_model.pickle"))


def _coerce_locale(locale: Optional[Locale]) -> Locale:
    if locale is None:
        return Locale('de-DE')
    if isinstance(locale, Locale):
        return Locale(locale.get_locale())
    return Locale(locale)


def _build_parser(
    locale: Optional[Locale] = None,
    base_date: Optional[datetime] = None,
    threshold: float = 0.5,
) -> DeDateParser:
    settings = {
        'PREFER_DAY_OF_MONTH': 'first',
        'STRICT_PARSING': False,
        'DATE_ORDER': 'DMY',
    }
    if base_date is not None:
        settings['RELATIVE_BASE'] = base_date
    return DeDateParser(
        DATE_MODEL_CHARS,
        enable_classifier_check=True,
        locale=_coerce_locale(locale),
        dateparser_settings=settings,
        classifier_model=MODEL_DATE,
        classifier_threshold=threshold,
        alphabet_character_set=DE_ALPHA_CHAR_SET,
        count_words=True,
        feature_window=0,
    )


# Retained for callers which inspect parser configuration directly. Public
# extraction functions use a fresh parser so concurrent calls cannot share
# mutable text, locale or result state.
parser = _build_parser()


def get_dates(
    text: str = None,
    locale: Optional[Locale] = None,
) -> Generator[dict, None, None]:
    yield from _build_parser(locale=locale).get_dates(
        text=text,
        locale=_coerce_locale(locale),
    )


def get_date_list(
    text: str = None,
    locale: Optional[Locale] = None,
) -> List[dict]:
    return list(get_dates(text=text, locale=locale))


def get_date_annotations(
    text: str = None,
    locale: Optional[Locale] = None,
    strict: bool = True,
    base_date: Optional[datetime] = None,
    threshold: float = 0.5,
) -> Generator[DateAnnotation, None, None]:
    locale_obj = _coerce_locale(locale)
    yield from _build_parser(
        locale=locale_obj,
        base_date=base_date,
        threshold=threshold,
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
) -> List[DateAnnotation]:
    return list(
        get_date_annotations(
            text=text,
            locale=locale,
            strict=strict,
            base_date=base_date,
            threshold=threshold,
        )
    )
