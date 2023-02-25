# -*- coding: utf-8 -*-

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Generator

from lexnlp.extract.all_locales.languages import LANG_EN, LANG_DE, DEFAULT_LANGUAGE, Locale
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
    routine = ROUTINE_BY_LOCALE.get(Locale(locale).language, ROUTINE_BY_LOCALE[DEFAULT_LANGUAGE.code])
    yield from routine(text, extended_sources, float_digits)
