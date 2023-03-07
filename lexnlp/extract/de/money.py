"""
Money extraction for English.
This module implements basic money extraction functionality in English.
Todo:
  * Improved unit tests and case coverage
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from collections import OrderedDict
from typing import Generator, List, Tuple, Union

from lexnlp.extract.common.money_detector import MoneyDetector
from lexnlp.extract.common.annotations.money_annotation import MoneyAnnotation
from lexnlp.extract.de.amounts import CURRENCY_PREFIX_MAP, CURRENCY_SYMBOL_MAP, amount_parser, get_amounts


CURRENCY_TOKEN_MAP = OrderedDict([
    ('chinesische yuan', 'CNY'),
    ('chinesischer yuan', 'CNY'),
    ('dollars', 'USD'),
    ('dollar', 'USD'),
    ('euros', 'EUR'),
    ('euro', 'EUR'),
    ('pfunde', 'GBP'),
    ('pfund', 'GBP'),
    ('renminbi', 'CNY'),
    ('yens', 'JPY'),
    ('yen', 'JPY'),
    ('yuans', 'CNY'),
    ('yuan', 'CNY'),
    ('deutsche mark', 'DEM')
])

TRIGGER_WORDS = ['preis', 'kosten']

money_detector = MoneyDetector(
    'de',
    'EUR',
    CURRENCY_TOKEN_MAP,
    CURRENCY_SYMBOL_MAP,
    CURRENCY_PREFIX_MAP,
    amount_parser.NUM_PTN,
    TRIGGER_WORDS,
    get_amounts
)


def get_money(
    text: str,
    return_sources: bool = False,
    float_digits: int = 4,
) -> Generator[Union[Tuple[str, str, str], Tuple[str, str]], None, None]:
    """
    """
    yield from money_detector.get_money(text, return_sources, float_digits)


def get_money_list(
    text: str,
    return_sources: bool = False,
    float_digits: int = 4,
) -> List[Union[Tuple[str, str, str], Tuple[str, str]]]:
    return list(money_detector.get_money(text, return_sources, float_digits))


def get_money_annotations(
    text: str,
    float_digits: int = 4,
) -> Generator[MoneyAnnotation, None, None]:
    """
    """
    yield from money_detector.get_money_annotations(text, float_digits)


def get_money_annotation_list(
    text: str,
    float_digits: int = 4,
) -> List[MoneyAnnotation]:
    return list(money_detector.get_money_annotations(text, float_digits))
