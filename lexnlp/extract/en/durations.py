"""Duration extraction for English.

This module implements duration extraction functionality in English.

Todo:
"""

from typing import Generator

# Imports
import regex as re

from lexnlp.extract.en.amounts import get_amounts, NUM_PTN

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

DURATION_MAP = {
    "second": 1 / (60 * 60 * 24),
    "minute": 1 / (60 * 24),
    "hour": 1 / 24,
    "day": 1,
    "week": 7,
    "month": 30,  # 365.25/12.,
    "quarter": 365 / 4,
    "year": 365,  # 365.25,
    "annum": 365,
    "anniversary": 365,
    "anniversaries": 365
}

DURATION_PTN = r"""
(({num_ptn})
(?:\s*(?:calendar|business|actual))?[\s-]*
({duration_list})s?)(?:\W|$)
""".format(
    num_ptn=NUM_PTN,
    duration_list='|'.join(DURATION_MAP)
)
DURATION_PTN_RE = re.compile(DURATION_PTN, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)


def get_durations(text, return_sources=False, float_digits=4) -> Generator:
    for source_text, number_text, duration_type in DURATION_PTN_RE.findall(text.lower()):
        amount = list(get_amounts(number_text, float_digits=float_digits))
        if len(amount) != 1:
            continue
        amount = amount[0]
        if float_digits:
            amount = round(amount, float_digits)
        duration_days = DURATION_MAP[duration_type] * amount
        if duration_type == 'anniversaries':
            duration_type = 'anniversary'
        item = (duration_type, amount, duration_days)
        if return_sources:
            item += (source_text.strip(),)
        yield item
