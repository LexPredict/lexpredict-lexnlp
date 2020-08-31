"""Distance extraction for English.

This module implements basic distance extraction functionality in English.

"""

# Imports
import re
from typing import Generator

from lexnlp.extract.common.annotations.distance_annotation import DistanceAnnotation
from lexnlp.extract.en.amounts import get_amounts, NUM_PTN

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


DISTANCE_SYMBOL_MAP = {
    "km": "kilometer",
    "mi": "mile",
}

DISTANCE_TOKEN_MAP = {
    "kilometers": "kilometer",
    "kilometer": "kilometer",
    "miles": "mile",
    "mile": "mile",
}

DISTANCE_PTN = r"""
(({num_ptn})\s*
({distance_tokens}|{distance_symbols}))(?:\W|$)
""".format(
    num_ptn=NUM_PTN.replace('(?:\\W|$)', '').replace('(?<=\\W|^)', ''),
    distance_symbols='|'.join(DISTANCE_SYMBOL_MAP),
    distance_tokens='|'.join(DISTANCE_TOKEN_MAP)
)
DISTANCE_PTN_RE = re.compile(DISTANCE_PTN, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)


def get_distances(text: str, return_sources=False, float_digits=4) -> Generator:
    for ant in get_distance_annotations(text, float_digits):
        item = (ant.amount, ant.distance_type)
        if return_sources:
            item += (ant.text,)
        yield item


def get_distance_annotations(text: str, float_digits=4) \
        -> Generator[DistanceAnnotation, None, None]:

    for match in DISTANCE_PTN_RE.finditer(text.lower()):
        source_text, number_text, distance_item = match.groups()
        amount = list(get_amounts(number_text, float_digits=float_digits))
        if len(amount) != 1:
            continue
        distance_type = DISTANCE_SYMBOL_MAP.get(distance_item) \
                        or DISTANCE_TOKEN_MAP.get(distance_item)
        amount = amount[0]
        if float_digits:
            amount = round(amount, float_digits)
        ant = DistanceAnnotation(coords=match.span(),
                                 amount=amount,
                                 distance_type=distance_type,
                                 text=source_text.strip())
        yield ant
