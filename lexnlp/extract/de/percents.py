__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import regex as re
from typing import Generator, List
from decimal import Decimal
from lexnlp.extract.common.annotations.percent_annotation import PercentAnnotation
from lexnlp.extract.de.amounts import AmountParserDE


amounts_parser = AmountParserDE()
get_amounts = amounts_parser.parse


PERCENT_UNITS_MAP = {
    'prozent': Decimal(0.01),
    '%': Decimal(0.01),
}

PERCENT_PTN = r"""
(?P<text>(?P<num_text>{num_ptn})\s*(?P<unit_name>\w*prozent|%))(?:\W|$)
""".format(num_ptn=amounts_parser.NUM_PTN)
PERCENT_PTN_RE = re.compile(PERCENT_PTN, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)


def get_percents(text: str, float_digits: int = 4) -> Generator[dict, None, None]:
    """
    Get percent usages within text.
    :param text:
    :param return_sources:
    :param float_digits:
    :return:
    """
    for ant in get_percent_annotations(text, float_digits):
        yield dict(
                location_start=ant.coords[0],
                location_end=ant.coords[1],
                source_text=ant.text,
                unit_name=ant.sign,
                amount=ant.amount,
                real_amount=ant.fraction)


def get_percent_annotations(
    text: str,
    float_digits: int = 4
) -> Generator[PercentAnnotation, None, None]:
    """
    Get percent usages within text.
    :param text:
    :param return_sources:
    :param float_digits:
    :return:
    """
    for match in PERCENT_PTN_RE.finditer(text):
        capture = match.capturesdict()
        amount_text = ''.join(capture.get('num_text', ''))
        unit_name = ''.join(capture.get('unit_name', ''))
        amount = list(get_amounts(amount_text, float_digits=float_digits))
        if len(amount) != 1:
            continue
        amount = amount[0]
        if 'prozent' in unit_name.lower():
            unit_name = 'prozent'
        real_amount = PERCENT_UNITS_MAP.get(unit_name, Decimal(0)) * amount

        if float_digits:
            real_amount = round(amount, float_digits)

        yield PercentAnnotation(
            coords=match.span(),
            text=''.join(capture.get('text', '')),
            sign=unit_name,
            amount=amount,
            fraction=real_amount,
            locale='de'
        )


def get_percent_list(text: str, float_digits: int = 4) -> List[dict]:
    return list(get_percents(text, float_digits))


def get_percent_annotation_list(
    text: str,
    float_digits: int = 4,
) -> List[PercentAnnotation]:
    return list(get_percent_annotations(text, float_digits))
