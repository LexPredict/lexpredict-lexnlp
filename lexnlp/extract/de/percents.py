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


PERCENT_UNITS_MAP = {
    'prozent': 0.01,
    '%': 0.01
}

PERCENT_PTN = r"""
(?P<text>(?P<num_text>{num_ptn})\s*(?P<unit_name>\w*prozent|%))(?:\W|$)
""".format(num_ptn=amounts_parser.NUM_PTN)
PERCENT_PTN_RE = re.compile(PERCENT_PTN, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)


def get_percents(text, float_digits=4) -> Generator:
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
        else:
            amount = amount[0]
        if 'prozent' in unit_name.lower():
            unit_name = 'prozent'
        real_amount = PERCENT_UNITS_MAP.get(unit_name, 0) * amount
        if float_digits:
            real_amount = round(amount, float_digits)
        yield dict(
                location_start=match.start(),
                location_end=match.end(),
                source_text=''.join(capture.get('text', '')),
                unit_name=unit_name,
                amount=amount,
                real_amount=real_amount)


def get_percent_list(*args, **kwargs):
    return list(get_percents(*args, **kwargs))
