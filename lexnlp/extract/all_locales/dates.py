# -*- coding: utf-8 -*-

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from datetime import datetime
from typing import Generator, Optional

from lexnlp.extract.all_locales.languages import (
    DEFAULT_LANGUAGE,
    LANG_DE,
    LANG_EN,
    LANG_ES,
    Locale,
    get_language_routine,
)
from lexnlp.extract.common.annotations.date_annotation import DateAnnotation
from lexnlp.extract.en.dates import get_date_annotations as get_date_annotations_en
from lexnlp.extract.de.dates import get_date_annotations as get_date_annotations_de
from lexnlp.extract.es.dates import get_date_annotations as get_date_annotations_es


ROUTINE_BY_LOCALE = {
    LANG_EN.code: get_date_annotations_en,
    LANG_DE.code: get_date_annotations_de,
    LANG_ES.code: get_date_annotations_es,
}


def get_date_annotations(locale: str,
                         text: str,
                         strict: Optional[bool] = None,
                         base_date: Optional[datetime] = None,
                         threshold: float = 0.50) -> Generator[DateAnnotation, None, None]:
    language = Locale(locale).language
    routine = get_language_routine(
        locale,
        ROUTINE_BY_LOCALE,
        DEFAULT_LANGUAGE,
    )
    strict = False if strict is None else strict
    yield from routine(
        text=text,
        strict=strict,
        locale=(
            Locale(locale)
            if language in ROUTINE_BY_LOCALE and language != LANG_EN.code
            else locale
        ),
        base_date=base_date,
        threshold=threshold,
    )
