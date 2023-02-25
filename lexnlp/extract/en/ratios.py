"""Ratio extraction for English.

This module implements ratio extraction functionality in English.

Todo:
  * Improved unit tests and case coverage
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from decimal import Decimal
import regex as re
from typing import Generator, Union, Tuple, List
from lexnlp.extract.common.annotations.ratio_annotation import RatioAnnotation
from lexnlp.extract.en.amounts import get_amounts, NUM_PTN


RATIO_PTN = r"""
(({num_ptn_1})\s*
(?:to|\:|/)\s*
({num_ptn_2}))(?!\s*[ap].?m(?:\W|$))
""".format(
    num_ptn_1=NUM_PTN.replace('(?:(?:no|\\d{1,2})/100)?', '').replace('(?:\\W|$)', ''),
    num_ptn_2=NUM_PTN.replace('(?:(?:no|\\d{1,2})/100)?', '')
)
RATIO_PTN_RE = re.compile(RATIO_PTN, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)


def get_ratios(
    text: str,
    return_sources: bool = False,
    float_digits: int = 4,
) -> Generator[Union[Tuple[Decimal, Decimal, Decimal], Tuple[Decimal, Decimal, Decimal, str]], None, None]:
    for ant in get_ratio_annotations(text, float_digits=float_digits):
        if return_sources:
            yield ant.left, ant.right, ant.ratio, ant.text
        else:
            yield ant.left, ant.right, ant.ratio


def get_ratio_list(
    text: str,
    return_sources: bool = False,
    float_digits: int = 4,
) -> List[Union[Tuple[Decimal, Decimal, Decimal], Tuple[Decimal, Decimal, Decimal, str]]]:
    """
    """
    return list(get_ratios(text, return_sources, float_digits))


def get_ratio_annotations(
    text: str,
    float_digits: int = 4,
) -> Generator[RatioAnnotation, None, None]:
    for match in RATIO_PTN_RE.finditer(text.lower()):
        source_text, ratio_1_text, ratio_2_text = match.groups()
        amount_1: List[Decimal] = \
            list(get_amounts(ratio_1_text, float_digits=float_digits))
        amount_2: List[Decimal] = \
            list(get_amounts(ratio_2_text, float_digits=float_digits))
        if len(amount_1) != 1 or len(amount_2) != 1:
            continue
        amount_1: Decimal = amount_1[0]
        amount_2: Decimal = amount_2[0]
        if amount_1 == 0 or amount_2 == 0:
            continue
        total = amount_1 / amount_2
        ant = RatioAnnotation(
            coords=match.span(),
            text=source_text.strip(),
            left=amount_1,
            right=amount_2,
            ratio=total
        )
        yield ant


def get_ratio_annotation_list(
    text: str,
    float_digits: int = 4,
) -> List[RatioAnnotation]:
    return list(get_ratio_annotations(text, float_digits))
