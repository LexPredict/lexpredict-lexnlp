# -*- coding: utf-8 -*-

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Generator

from lexnlp.extract.all_locales.languages import LANG_EN, LANG_DE, DEFAULT_LANGUAGE, Locale
from lexnlp.extract.common.annotations.money_annotation import MoneyAnnotation
from lexnlp.extract.en.money import get_money_annotations as get_money_annotations_en
from lexnlp.extract.de.money import get_money_annotations as get_money_annotations_de


ROUTINE_BY_LOCALE = {
    LANG_EN.code: get_money_annotations_en,
    LANG_DE.code: get_money_annotations_de
}


def get_money_annotations(
    locale: str,
    text: str,
    float_digits: int = 4,
) -> Generator[MoneyAnnotation, None, None]:
    routine = ROUTINE_BY_LOCALE.get(Locale(locale).language, ROUTINE_BY_LOCALE[DEFAULT_LANGUAGE.code])
    yield from routine(text, float_digits)
