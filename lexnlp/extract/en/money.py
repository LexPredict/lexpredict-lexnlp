"""Money extraction for English.

This module implements basic money extraction functionality in English.

Todo:
  * Improved unit tests and case coverage
"""

# Imports
import regex as re
import string
from collections import OrderedDict
from typing import Generator

from lexnlp.extract.common.annotations.money_annotation import MoneyAnnotation
from lexnlp.extract.en.amounts import (
    get_amounts, NUM_PTN, CURRENCY_PREFIX_MAP,
    CURRENCY_SYMBOL_MAP)

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


DEFAULT_CURRENCY = 'USD'

CURRENCY_TOKEN_MAP = OrderedDict([
    ('chinese yuans', 'CNY'),
    ('chinese yuan', 'CNY'),
    ('dollars', 'USD'),
    ('dollar', 'USD'),
    ('euros', 'EUR'),
    ('euro', 'EUR'),
    ('pounds', 'GBP'),
    ('pound', 'GBP'),
    ('renminbi', 'CNY'),
    ('yens', 'JPY'),
    ('yen', 'JPY'),
    ('yuans', 'CNY'),
    ('yuan', 'CNY')
])

CURRENCY_ABBR_LIST = set(
    list(CURRENCY_SYMBOL_MAP.values()) +
    list(CURRENCY_TOKEN_MAP.values()) +
    list(CURRENCY_PREFIX_MAP.values())
)

CURRENCY_PREFIXES = set(
    list(CURRENCY_PREFIX_MAP.keys()) +
    list(CURRENCY_SYMBOL_MAP.values())
)

CURR_NUM_PTN = NUM_PTN.replace('(?<=\\W|^)', '')

TRIGGER_WORDS = ['price', 'cost']

CURRENCY_PTN = r"""
(?P<text>
    (?P<prefix>{currency_prefixes}|[{currency_symbols}])\s*
    (?P<amount>{num_ptn_1})
    |
    (?P<amount>{num_ptn_2})\s*
    (?P<postfix>{currency_tokens}|{currency_abbreviations})(?:\W|$)
    |
    (?:\W|^)(?P<trigger_word>{trigger_words})\s[^\d]{{,100}}(?P<amount>\d+(?:\.\d{{1,2}})?)
)
""".format(
    num_ptn_1=CURR_NUM_PTN,
    num_ptn_2=CURR_NUM_PTN,
    currency_prefixes='|'.join(CURRENCY_PREFIXES),
    currency_symbols=''.join([re.escape(i) for i in CURRENCY_SYMBOL_MAP]),
    currency_tokens='|'.join([i.replace(' ', '\\s+') for i in CURRENCY_TOKEN_MAP]),
    currency_abbreviations='|'.join(CURRENCY_ABBR_LIST),
    trigger_words='|'.join(TRIGGER_WORDS)
)
CURRENCY_PTN_RE = re.compile(CURRENCY_PTN, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)


def get_money(text: str, return_sources=False, float_digits=4) -> Generator:
    for ant in get_money_annotations(text, float_digits):
        item = (ant.amount, ant.currency)
        if return_sources:
            item += (ant.text,)
        yield item


def get_money_annotations(text: str, float_digits=4) \
        -> Generator[MoneyAnnotation, None, None]:
    for match in CURRENCY_PTN_RE.finditer(text):
        capture = match.capturesdict()
        if not (capture['prefix'] or capture['postfix']) and not (capture['trigger_word']):
            continue
        prefix = capture['prefix']
        postfix = capture['postfix']
        amount = list(get_amounts(capture['amount'][0], float_digits=float_digits))
        if len(amount) != 1:
            continue
        if prefix:
            prefix = prefix[0].lower()
            currency_type = CURRENCY_SYMBOL_MAP.get(prefix)\
                            or CURRENCY_PREFIX_MAP.get(prefix)\
                            or prefix.upper()
        elif postfix:
            postfix = postfix[0].lower()
            currency_type = CURRENCY_TOKEN_MAP.get(postfix) or (capture['postfix'][0]).upper()
        else:
            currency_type = None
        if not currency_type:
            currency_type = DEFAULT_CURRENCY
        text = capture['text'][0].strip(
                   string.punctuation.replace('$', '') + string.whitespace)
        ant = MoneyAnnotation(coords=match.span(),
                              amount=amount[0],
                              text=text,
                              currency=currency_type)
        yield ant
