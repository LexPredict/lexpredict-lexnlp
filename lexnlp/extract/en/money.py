"""Money extraction for English.

This module implements basic money extraction functionality in English.

Todo:
  * Improved unit tests and case coverage
"""

# Imports
import regex as re

from lexnlp.extract.en.amounts import get_amounts, NUM_PTN

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

CURRENCY_SYMBOL_MAP = {
    "$": "USD",
    "€": "EUR",
    "¥": "JPY",
    "£": "GBP",
    "₠": "EUR",
    "₨": "INR",
    "₹": "INR",
    "₺": "TRY",
    "元": "CNY",
    "₽": "RUB",
    # "¢": None,
    "₩": "KRW",
}

CURRENCY_TOKEN_MAP = {
    "dollar": "USD",
    "dollars": "USD",
    "euro": "EUR",
    "euros": "EUR",
    "pound": "GBP",
    "yen": "JPY",
    "renminbi": "CNY",
    "yuan": "CNY",
    "chinese yuan": "CNY",
}

CURRENCY_PREFIX_MAP = {
    "chf": "CHF",
    "rmb": "CNY",
}

CURRENCY_ABBR_LIST = set(
    list(CURRENCY_SYMBOL_MAP.values()) +
    list(CURRENCY_TOKEN_MAP.values()) +
    list(CURRENCY_PREFIX_MAP.values())
)

CURRENCY_PTN = r"""
(?P<text>
(?P<prefix>{currency_prefixes}|[{currency_symbols}])\s*
(?P<amount>{num_ptn_1})
|
(?P<amount>{num_ptn_2})\s*
(?P<postfix>{currency_tokens}|{currency_abbreviations}))
""".format(
    num_ptn_1=NUM_PTN,
    num_ptn_2=NUM_PTN,
    currency_prefixes='|'.join(CURRENCY_PREFIX_MAP),
    currency_symbols=''.join([re.escape(i) for i in CURRENCY_SYMBOL_MAP]),
    currency_tokens='|'.join([i.replace(' ', '\\s+') for i in CURRENCY_TOKEN_MAP]),
    currency_abbreviations='|'.join(CURRENCY_ABBR_LIST),
)
CURRENCY_PTN_RE = re.compile(CURRENCY_PTN, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)


def get_money(text, return_sources=False, float_digits=4):
    result = []
    for match in CURRENCY_PTN_RE.finditer(text):
        capture = match.capturesdict()
        if not (capture['prefix'] or capture['postfix']):
            continue
        prefix = capture['prefix']
        postfix = capture['postfix']
        amount = get_amounts(capture['amount'][0], float_digits=float_digits)
        if len(amount) != 1:
            continue
        if prefix:
            prefix = prefix[0].lower()
            currency_type = CURRENCY_SYMBOL_MAP.get(prefix) or CURRENCY_PREFIX_MAP.get(prefix)
        else:
            postfix = postfix[0].lower()
            currency_type = CURRENCY_TOKEN_MAP.get(postfix) or capture['postfix'][0]
        item = (amount[0], currency_type)
        if return_sources:
            item += (capture['text'][0].strip(),)
        result.append(item)
    return result
