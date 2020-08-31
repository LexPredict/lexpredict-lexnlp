"""Ratio extraction for English.

This module implements ratio extraction functionality in English.

Todo:
  * Improved unit tests and case coverage
"""

# Imports
import regex as re
from typing import Generator

from lexnlp.extract.common.annotations.ratio_annotation import RatioAnnotation
from lexnlp.extract.en.amounts import get_amounts, NUM_PTN

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


RATIO_PTN = r"""
(({num_ptn_1})\s*
(?:to|\:|/)\s*
({num_ptn_2}))(?!\s*[ap].?m(?:\W|$))
""".format(
    num_ptn_1=NUM_PTN.replace('(?:(?:no|\\d{1,2})/100)?', '').replace('(?:\\W|$)', ''),
    num_ptn_2=NUM_PTN.replace('(?:(?:no|\\d{1,2})/100)?', '')
)
RATIO_PTN_RE = re.compile(RATIO_PTN, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)


def get_ratios(text: str, return_sources=False, float_digits=4) \
    -> Generator:
    for ant in get_ratio_annotations(text, float_digits=float_digits):
        item = (ant.left, ant.right, ant.ratio)
        if return_sources:
            item += (ant.text,)
        yield item


def get_ratio_annotations(text: str, float_digits=4) \
        -> Generator[RatioAnnotation, None, None]:
    for match in RATIO_PTN_RE.finditer(text.lower()):
        source_text, ratio_1_text, ratio_2_text = match.groups()
        amount_1 = list(get_amounts(ratio_1_text, float_digits=float_digits))
        amount_2 = list(get_amounts(ratio_2_text, float_digits=float_digits))
        if len(amount_1) != 1 or len(amount_2) != 1:
            continue
        amount_1 = amount_1[0]
        amount_2 = amount_2[0]
        if amount_1 == 0 or amount_2 == 0:
            continue
        if float_digits:
            amount_1 = round(amount_1, float_digits)
            amount_2 = round(amount_2, float_digits)
        total = float(amount_1) / amount_2
        ant = RatioAnnotation(coords=match.span(),
                              text=source_text.strip(),
                              left=amount_1,
                              right=amount_2,
                              ratio=total)
        yield ant
