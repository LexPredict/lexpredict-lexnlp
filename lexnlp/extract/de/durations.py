__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import regex as re
from typing import Generator, List
from decimal import Decimal
from fractions import Fraction
from lexnlp.extract.common.durations.durations_parser import DurationParser
from lexnlp.extract.common.annotations.duration_annotation import DurationAnnotation
from lexnlp.extract.de.amounts import AmountParserDE
from lexnlp.extract.en.amounts import quantize_by_float_digit


amounts_parser = AmountParserDE()
get_amounts = amounts_parser.parse


class DeDurationParser(DurationParser):
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

    DURATION_TRANSLATION_MAP = {
        "sekunde": 'second',
        "sekunden": 'second',
        "minute": 'minute',
        "minuten": 'minute',
        "stunde": 'hour',
        "stunden": 'hour',
        "tag": 'day',
        "tage": 'day',
        "woche": 'week',
        "wochen": 'week',
        "monat": 'month',
        "monate": 'month',
        "vierteljahr": 'quarter',
        "vierteljahre": 'quarter',
        "jahr": 'year',
        "jahre": 'year',
        "jahres": 'year',
        "jahren": 'year',
    }

    duration_items = sorted(DURATION_TRANSLATION_MAP.keys(), key=len, reverse=True)
    duration_items_joined = '|'.join(duration_items)
    DURATION_MAP_RE = re.compile(duration_items_joined)

    DURATION_PTN = r"""
    (?P<text>(?P<num_text>{num_ptn})?
    (?P<unit_prefix>(?:kalend[ae]r|lebens|actual))?
    (?P<unit_name>{unit_names}))
    (?:\W|$)
    """.format(num_ptn=amounts_parser.NUM_PTN, unit_names=duration_items_joined)

    DURATION_PTN_RE = re.compile(DURATION_PTN, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)

    INNER_CONJUNCTIONS = ['und', 'plus']

    INNER_PUNCTUATION = re.compile(r'[\s\,]')

    LOCALE = 'de'

    @classmethod
    def get_all_annotations(
        cls,
        text: str,
        float_digits: int = 4
    ) -> List[DurationAnnotation]:
        all_annotations: List[DurationAnnotation] = []
        for match in cls.DURATION_PTN_RE.finditer(text):
            capture = match.capturesdict()
            amount_text = ''.join(capture.get('num_text', ''))
            amounts = list(get_amounts(amount_text, float_digits=float_digits))
            if len(amounts) != 1:
                amount = Decimal('1.0')
            else:
                amount = amounts[0]
            unit_name_local = ''.join(capture.get('unit_name', '')).lower()
            unit_prefix = ''.join(capture.get('unit_prefix', '')).lower()
            unit_name_local = cls.DURATION_MAP_RE.findall(unit_name_local)
            if not unit_name_local:
                continue
            unit_name_local = unit_name_local[0]
            unit_name_en = cls.DURATION_TRANSLATION_MAP.get(unit_name_local)

            _duration_fraction: Fraction = cls.DURATION_MAP[unit_name_en]
            amount_days: Decimal = Decimal(
                (_duration_fraction.numerator * amount)
                / _duration_fraction.denominator
            )

            if float_digits:
                amount_days: Decimal = quantize_by_float_digit(
                    amount=amount_days,
                    float_digits=float_digits
                )

            ant: DurationAnnotation = DurationAnnotation(
                coords=match.span(),
                text=''.join(capture.get('text', '')),
                amount=amount,
                duration_days=amount_days,
                duration_type_en=unit_name_en,
                duration_type=unit_name_local,
                prefix=unit_prefix,
                locale=cls.LOCALE,
                value_dict={unit_name_en: float(amount)}
            )
            all_annotations.append(ant)
        return all_annotations


def get_durations(text: str, float_digits: int = 4) -> Generator:
    for ant in DeDurationParser.get_annotations(text, float_digits):
        yield dict(
                location_start=ant.coords[0],
                location_end=ant.coords[1],
                source_text=ant.text,
                unit_name_local=ant.duration_type,
                unit_name=ant.duration_type_en,
                unit_prefix=ant.prefix,
                amount=ant.amount,
                amount_days=ant.duration_days)


def get_duration_annotations(
    text: str,
    float_digits: int = 4
) -> Generator[DurationAnnotation, None, None]:
    yield from DeDurationParser.get_annotations(text, float_digits)


def get_duration_annotations_list(
    text: str,
    float_digits: int = 4
) -> List[DurationAnnotation]:
    return DeDurationParser.get_annotations(text, float_digits)


def get_duration_list(text: str, float_digits: int = 4) -> List:
    return list(get_durations(text, float_digits))
