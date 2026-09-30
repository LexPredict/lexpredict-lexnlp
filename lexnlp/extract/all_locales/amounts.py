# -*- coding: utf-8 -*-

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Generator

from lexnlp.extract.all_locales.languages import (
    DEFAULT_LANGUAGE,
    LANG_DE,
    LANG_EN,
    Locale,
    get_language_routine,
)
from lexnlp.extract.common.annotations.amount_annotation import AmountAnnotation
from lexnlp.extract.en.amounts import get_amount_annotations as get_amount_annotations_en
from lexnlp.extract.de.amounts import get_amount_annotations as get_amount_annotations_de


ROUTINE_BY_LOCALE = {
    LANG_EN.code: get_amount_annotations_en,
    LANG_DE.code: get_amount_annotations_de
}


def get_amount_annotations(
    locale: str,
    text: str,
    extended_sources: bool = True,
    float_digits: int = 4,
) -> Generator[AmountAnnotation, None, None]:
    language = Locale(locale).language
    routine = get_language_routine(
        locale,
        ROUTINE_BY_LOCALE,
        DEFAULT_LANGUAGE,
    )
    if language == LANG_DE.code:
        yield from routine(
            text=text,
            float_digits=float_digits,
            return_sources=extended_sources,
        )
    else:
        yield from routine(
            text=text,
            extended_sources=extended_sources,
            float_digits=float_digits,
        )
