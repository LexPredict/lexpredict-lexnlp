"""Percent extraction for English.

This module implements percent extraction functionality in English.
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import regex as re
from decimal import Decimal
from typing import Dict, Generator, List, Tuple, Union

from lexnlp.extract.en.ratios import get_ratio_annotations
from lexnlp.extract.common.annotations.percent_annotation import PercentAnnotation
from lexnlp.extract.common.annotations.ratio_annotation import RatioAnnotation
from .amounts import get_amounts, NUM_PTN, quantize_by_float_digit
from .money import CURRENCY_SYMBOL_MAP, CURRENCY_PREFIX_MAP


PERCENT_UNIT_MAP: Dict[str, Decimal] = {
    "%": Decimal('0.01'),
    "percent": Decimal('0.01'),
    "percents": Decimal('0.01'),
    "percentage point": Decimal('0.01'),
    "percentage points": Decimal('0.01'),
    "bps": Decimal('0.0001'),
    "basis point": Decimal('0.0001'),
    "basis points": Decimal('0.0001')
}

PERCENT_UNIT_LIST: List[str] = list(PERCENT_UNIT_MAP.keys())
PERCENT_UNIT_LIST.sort(key=len, reverse=True)

PERCENT_PTN = r"""
(({num_ptn})[\s\)]*({percent_units}))(?:\W|$)
""".format(num_ptn=NUM_PTN.replace("(?:\\W|$)", '')
           .replace("[\\.\\d][\\d\\.,]", "((?:{currency_prefixes}|[{currency_symbols}])\\s*)?[\\.\\d][\\d\\.,]"
                    .format(currency_prefixes='|'.join(CURRENCY_PREFIX_MAP),
                            currency_symbols=''.join([re.escape(i) for i in CURRENCY_SYMBOL_MAP]))),
           percent_units='|'.join([re.escape(i) for i in PERCENT_UNIT_LIST]))
PERCENT_PTN_RE = re.compile(PERCENT_PTN, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)


def get_percents(
    text: str,
    return_sources: bool = False,
    float_digits: int = 4,
) -> Generator[Union[Tuple[str, Decimal, Decimal], Tuple[str, Decimal, Decimal, str]], None, None]:
    """
    Get percent usages within text.
    :param text:
    :param return_sources:
    :param float_digits:
    :return:
    """
    ant: PercentAnnotation
    for ant in get_percent_annotations(text, float_digits):
        if return_sources:
            yield ant.sign, ant.amount, ant.fraction, ant.text
        else:
            yield ant.sign, ant.amount, ant.fraction


def get_percent_list(
    text: str,
    return_sources: bool = False,
    float_digits: int = 4,
) -> List[Union[Tuple[str, Decimal, Decimal], Tuple[str, Decimal, Decimal, str]]]:
    """
    """
    return list(get_percents(text, return_sources, float_digits))


def get_percent_annotations(
    text: str,
    float_digits: int = 4,
) -> Generator[PercentAnnotation, None, None]:
    """
    Get percent usages within text.
    """
    for match in PERCENT_PTN_RE.finditer(text.lower()):
        source_text, number_text, currency_prefix, percent_item = match.groups()
        if currency_prefix:
            continue

        numbers: List[Decimal] = \
            list(get_amounts(number_text, float_digits=float_digits))
        if len(numbers) == 1:
            val: Decimal = Decimal(str(numbers[0]))
        else:
            ratios: List[RatioAnnotation] = \
                list(get_ratio_annotations(number_text, float_digits=float_digits))
            if len(ratios) == 1:
                val: Decimal = Decimal(ratios[0].ratio)
            else:
                continue

        fraction: Decimal = PERCENT_UNIT_MAP[percent_item] * val

        if float_digits:
            fraction: Decimal = quantize_by_float_digit(
                amount=fraction,
                float_digits=float_digits
            )

        yield PercentAnnotation(
            coords=match.span(),
            text=source_text.strip(),
            amount=val,
            fraction=fraction,
            sign=percent_item
        )


def get_percent_annotation_list(
    text: str,
    float_digits: int = 4,
) -> List[PercentAnnotation]:
    """
    """
    return list(get_percent_annotations(text, float_digits))
