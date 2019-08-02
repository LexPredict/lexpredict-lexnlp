"""Percent extraction for English.

This module implements percent extraction functionality in English.

Todo:
"""

# Imports
import regex as re
from typing import Generator

from lexnlp.extract.common.annotations.percent_annotation import PercentAnnotation
from .amounts import get_amounts, NUM_PTN
from .money import CURRENCY_SYMBOL_MAP, CURRENCY_PREFIX_MAP

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.7"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


PERCENT_UNIT_MAP = {
    "percent": 0.01,
    "percents": 0.01,
    # "percentage": 0.01,
    "percentage point": 0.01,
    "percentage points": 0.01,
    "bps": 0.0001,
    "basis point": 0.0001,
    "basis points": 0.0001,
    "%": 0.01}
PERCENT_UNIT_LIST = list(PERCENT_UNIT_MAP.keys())
PERCENT_UNIT_LIST.sort(key=len, reverse=True)

PERCENT_PTN = r"""
(({num_ptn})[\s\)]*({percent_units}))(?:\W|$)
""".format(num_ptn=NUM_PTN.replace("(?:\\W|$)", '') \
           .replace("[\\.\\d][\\d\\.,]", "((?:{currency_prefixes}|[{currency_symbols}])\\s*)?[\\.\\d][\\d\\.,]" \
                    .format(currency_prefixes='|'.join(CURRENCY_PREFIX_MAP),
                            currency_symbols=''.join([re.escape(i) for i in CURRENCY_SYMBOL_MAP]), )),
           percent_units='|'.join([re.escape(i) for i in PERCENT_UNIT_LIST]))
PERCENT_PTN_RE = re.compile(PERCENT_PTN, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)


def get_percents(text: str, return_sources=False, float_digits=4) -> Generator:
    """
    Get percent usages within text.
    :param text:
    :param return_sources:
    :param float_digits:
    :return:
    """
    for ant in get_percent_annotations(text, float_digits):
        item = (ant.sign, ant.amount, ant.fraction)
        if return_sources:
            item += (ant.text,)
        yield item


def get_percent_annotations(text: str, float_digits=4) \
        -> Generator[PercentAnnotation, None, None]:
    """
    Get percent usages within text.
    """
    for match in PERCENT_PTN_RE.finditer(text.lower()):
        source_text, number_text, currency_prefix, percent_item = match.groups()
        if currency_prefix:
            continue
        number = list(get_amounts(number_text, float_digits=float_digits))
        if len(number) != 1:
            continue
        val = PERCENT_UNIT_MAP[percent_item] * number[0]
        if float_digits:
            val = round(val, float_digits)
        ant = PercentAnnotation(coords=match.span(),
                                text=source_text.strip(),
                                amount=number[0],
                                fraction=val,
                                sign=percent_item)
        yield ant
