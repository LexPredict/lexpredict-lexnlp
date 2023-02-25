"""Distance extraction for English.

This module implements basic distance extraction functionality in English.

"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import re
from decimal import Decimal
from typing import Generator, List, Tuple, Union

from lexnlp.extract.common.annotations.distance_annotation import DistanceAnnotation
from lexnlp.extract.en.amounts import get_amounts, NUM_PTN


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


def get_distances(
    text: str,
    return_sources: bool = False,
    float_digits: int = 4
) -> Generator[Union[Tuple[Decimal, str], Tuple[Decimal, str, str]], None, None]:
    for ant in get_distance_annotations(text, float_digits):
        if return_sources:
            yield ant.amount, ant.distance_type, ant.text
        else:
            yield ant.amount, ant.distance_type


def get_distance_list(
    text: str,
    return_sources: bool = False,
    float_digits: int = 4,
) -> List[Union[Tuple[Decimal, str], Tuple[Decimal, str, str]]]:
    """
    """
    return list(get_distances(text, return_sources, float_digits))


def get_distance_annotations(
    text: str,
    float_digits: int = 4
) -> Generator[DistanceAnnotation, None, None]:
    for match in DISTANCE_PTN_RE.finditer(text.lower()):
        source_text, number_text, distance_item = match.groups()
        amount = list(get_amounts(number_text, float_digits=float_digits))
        if len(amount) != 1:
            continue
        distance_type = DISTANCE_SYMBOL_MAP.get(distance_item) \
                        or DISTANCE_TOKEN_MAP.get(distance_item)
        yield DistanceAnnotation(
            coords=match.span(),
            amount=amount[0],
            distance_type=distance_type,
            text=source_text.strip()
        )


def get_distance_annotation_list(
    text: str,
    float_digits: int = 4,
) -> List[DistanceAnnotation]:
    """
    """
    return list(get_distance_annotations(text, float_digits))
