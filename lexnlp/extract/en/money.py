"""
Money extraction for English.
This module implements basic money extraction functionality in English.
Todo:
  * Improved unit tests and case coverage
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

from collections import OrderedDict
from typing import Generator, Union, Tuple

from lexnlp.extract.common.money_detector import MoneyDetector
from lexnlp.extract.common.annotations.money_annotation import MoneyAnnotation
from lexnlp.extract.en.amounts import NUM_PTN, CURRENCY_PREFIX_MAP, CURRENCY_SYMBOL_MAP, get_amounts


CURRENCY_TOKEN_MAP = OrderedDict([
    ('chinese yuans', 'CNY'),
    ('chinese yuan', 'CNY'),
    ('dollars', 'USD'),
    ('dollar', 'USD'),
    ('euros', 'EUR'),
    ('euro', 'EUR'),
    ('pounds', 'GBP'),
    ('pound', 'GBP'),
    ('renminbi', 'CNY'),
    ('yens', 'JPY'),
    ('yen', 'JPY'),
    ('yuans', 'CNY'),
    ('yuan', 'CNY')
])

TRIGGER_WORDS = ['price', 'cost']

money_detector = MoneyDetector(
    'en',
    'USD',
    CURRENCY_TOKEN_MAP,
    CURRENCY_SYMBOL_MAP,
    CURRENCY_PREFIX_MAP,
    NUM_PTN,
    TRIGGER_WORDS,
    get_amounts
)


def get_money(
        text: str,
        return_sources: bool = False,
        float_digits: int = 4) -> Generator[Union[Tuple[str, str, str], Tuple[str, str]], None, None]:
    yield from money_detector.get_money(text, return_sources, float_digits)


def get_money_annotations(
    text: str,
    float_digits: int = 4,
) -> Generator[MoneyAnnotation, None, None]:
    yield from money_detector.get_money_annotations(text, float_digits)
