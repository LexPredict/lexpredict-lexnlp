import regex as re
from typing import Generator

from lexnlp.extract.de.amounts import AmountParserDE


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


amounts_parser = AmountParserDE()
get_amounts = amounts_parser.parse


DURATION_MAP = {
    "second": 1 / (60 * 60 * 24),
    "minute": 1 / (60 * 24),
    "hour": 1 / 24,
    "day": 1,
    "week": 7,
    "month": 30,  # 365.25/12.,
    "quarter": 365 / 4,
    "year": 365,  # 365.25,
}

DURATION_TRANSLATION_MAP = {
    "secunde": 'second',
    "secunden": 'second',
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


def get_durations(text, float_digits=4) -> Generator:
    """
    Get duration usages within text.
    :param text:
    :param float_digits:
    :return:
    """
    for match in DURATION_PTN_RE.finditer(text):
        capture = match.capturesdict()
        amount_text = ''.join(capture.get('num_text', ''))
        amount = list(get_amounts(amount_text, float_digits=float_digits))
        if len(amount) != 1:
            amount = 1
        else:
            amount = amount[0]
        unit_name_local = ''.join(capture.get('unit_name', '')).lower()
        unit_prefix = ''.join(capture.get('unit_prefix', '')).lower()
        unit_name_local = DURATION_MAP_RE.findall(unit_name_local)
        if not unit_name_local:
            continue
        unit_name_local = unit_name_local[0]
        unit_name_en = DURATION_TRANSLATION_MAP.get(unit_name_local)

        amount_days = DURATION_MAP[unit_name_en] * amount
        if float_digits:
            amount_days = round(amount_days, float_digits)
        yield dict(
                location_start=match.start(),
                location_end=match.end(),
                source_text=''.join(capture.get('text', '')),
                unit_name_local=unit_name_local,
                unit_name=unit_name_en,
                unit_prefix=unit_prefix,
                amount=amount,
                amount_days=amount_days)


def get_duration_list(*args, **kwargs):
    return list(get_durations(*args, **kwargs))
