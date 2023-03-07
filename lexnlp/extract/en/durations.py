"""
This module implements duration extraction functionality in English.
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Generator, List, Union, Tuple
import regex as re
from decimal import Decimal
from fractions import Fraction
from lexnlp.extract.common.durations.durations_parser import DurationParser
from lexnlp.extract.common.annotations.duration_annotation import DurationAnnotation
from lexnlp.extract.en.amounts import get_amounts, quantize_by_float_digit, NUM_PTN


class EnDurationParser(DurationParser):
    DURATION_MAP = {
        "second": Fraction(1, (60 * 60 * 24)),
        "minute": Fraction(1, (60 * 24)),
        "hour": Fraction(1, 24),
        "day": Fraction(1),
        "week": Fraction(7),
        "month": Fraction(30),  # 365.25/12.,
        "quarter": Fraction(365, 4),
        "year": Fraction(365),  # 365.25,
        "annum": Fraction(365),
        "anniversary": Fraction(365),
        "anniversaries": Fraction(365),
    }

    DURATION_PTN = fr"(({NUM_PTN})(?:\s*(?:calendar|business|actual))?[\s-]*({'|'.join(DURATION_MAP)})s?(?!-))(?:\W|$)"
    DURATION_PTN_RE = re.compile(DURATION_PTN, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)

    INNER_CONJUNCTIONS = ['and', 'plus']
    INNER_PUNCTUATION = re.compile(r'[\s\,]')

    @classmethod
    def get_all_annotations(cls,
                            text: str,
                            float_digits: int = 4) -> List[DurationAnnotation]:
        all_annotations: List[DurationAnnotation] = []
        for match in cls.DURATION_PTN_RE.finditer(text.lower()):
            source_text, number_text, duration_type = match.groups()
            amount = list(get_amounts(number_text, float_digits=float_digits))
            if len(amount) != 1:
                continue
            amount = amount[0]
            _duration_fraction: Fraction = cls.DURATION_MAP[duration_type]
            duration_days: Decimal = Decimal(_duration_fraction.numerator * amount / _duration_fraction.denominator)
            if float_digits:
                duration_days: Decimal = quantize_by_float_digit(amount=duration_days,
                                                                 float_digits=float_digits)
            if duration_type == 'anniversaries':
                duration_type = 'anniversary'
            ant: DurationAnnotation = DurationAnnotation(coords=match.span(),
                                                         amount=amount,
                                                         duration_type=duration_type,
                                                         duration_days=duration_days,
                                                         text=source_text.strip(),
                                                         value_dict={duration_type: float(amount)})
            all_annotations.append(ant)
        return all_annotations


def get_durations(text: str,
                  return_sources: bool = False,
                  float_digits: int = 4) -> Generator[Union[Tuple[str, Decimal, Decimal],
                                                            Tuple[str, Decimal, Decimal, str]], None, None]:
    for ant in EnDurationParser.get_annotations(text, float_digits):
        yield (ant.duration_type, ant.amount, ant.duration_days, ant.text) \
            if return_sources else (ant.duration_type, ant.amount, ant.duration_days)


def get_duration_list(text: str,
                      return_sources: bool = False,
                      float_digits: int = 4) -> List[Union[Tuple[str, Decimal, Decimal],
                                                           Tuple[str, Decimal, Decimal, str]]]:
    return list(get_durations(text, return_sources, float_digits))


def get_duration_annotations(text: str, float_digits: int = 4) -> Generator[DurationAnnotation, None, None]:
    yield from EnDurationParser.get_annotations(text, float_digits)


def get_duration_annotations_list(text: str, float_digits: int = 4) -> List[DurationAnnotation]:
    return EnDurationParser.get_annotations(text, float_digits)
