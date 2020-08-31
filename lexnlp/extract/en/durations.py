"""
This module implements duration extraction functionality in English.
"""

from typing import Generator, List
import regex as re

from lexnlp.extract.common.durations.durations_parser import DurationParser
from lexnlp.extract.common.annotations.duration_annotation import DurationAnnotation
from lexnlp.extract.en.amounts import get_amounts, NUM_PTN

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class EnDurationParser(DurationParser):
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

    INNER_CONJUNCTIONS = ['and', 'plus']

    INNER_PUNCTUATION = re.compile(r'[\s\,]')

    @classmethod
    def get_all_annotations(cls,
                            text: str,
                            float_digits=4) \
            -> List[DurationAnnotation]:

        all_annotations = []

        for match in cls.DURATION_PTN_RE.finditer(text.lower()):
            source_text, number_text, duration_type = match.groups()
            amount = list(get_amounts(number_text, float_digits=float_digits))
            if len(amount) != 1:
                continue
            amount = amount[0]
            if float_digits:
                amount = round(amount, float_digits)
            duration_days = cls.DURATION_MAP[duration_type] * amount
            if duration_type == 'anniversaries':
                duration_type = 'anniversary'
            ant = DurationAnnotation(coords=match.span(),
                                     amount=amount,
                                     duration_type=duration_type,
                                     duration_days=duration_days,
                                     text=source_text.strip())
            all_annotations.append(ant)
        return all_annotations


def get_durations(text: str, return_sources=False, float_digits=4) -> Generator:
    for ant in EnDurationParser.get_annotations(text, float_digits):
        item = (ant.duration_type, ant.amount, ant.duration_days)
        if return_sources:
            item += (ant.text,)
        yield item


def get_duration_annotations(text: str,
                             float_digits=4) \
        -> Generator[DurationAnnotation, None, None]:
    yield from EnDurationParser.get_annotations(text, float_digits)


def get_duration_annotations_list(text: str,
                                  float_digits=4) \
        -> List[DurationAnnotation]:
    return EnDurationParser.get_annotations(text, float_digits)
