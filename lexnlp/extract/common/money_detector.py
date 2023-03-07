# -*- coding: utf-8 -*-

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from decimal import Decimal

import regex as re
import string
from typing import Generator, Dict, List, Tuple, Union, Callable

from lexnlp.extract.common.annotations.money_annotation import MoneyAnnotation


class MoneyDetector:
    def __init__(self,
                 locale: str,
                 default_currency: str,
                 currency_token_map: Dict[str, str],
                 currency_symbol_map,
                 currency_preffix_map: Dict[str, str],
                 num_ptn: str,
                 trigger_words: List[str],
                 get_amounts: Callable):
        self.locale = locale
        self.default_currency = default_currency  # 'USD' or ...
        self.currency_token_map = currency_token_map  # OrderedDict([('chinesische yuan', 'CNY'), ...
        self.currency_symbol_map = currency_symbol_map  # {"$": "USD", ...
        self.currency_preffix_map = currency_preffix_map  # {"rmb": "CNY", ...
        self.currency_abbr_list = set(
            list(currency_symbol_map.values()) +
            list(currency_token_map.values()) +
            list(currency_preffix_map.values())
        )
        self.currency_prefixes = set(
            list(currency_preffix_map.keys()) +
            list(currency_symbol_map.values())
        )
        self.curr_num_ptn = num_ptn.replace('(?<=\\W|^)', '')
        self.trigger_words = trigger_words  # ['price', 'cost']
        currency_ptrn = self.build_currency_pattern()
        self.currency_ptn_re = re.compile(currency_ptrn, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)
        self.get_amounts = get_amounts

    def build_currency_pattern(self) -> str:
        currency_prefixes = '|'.join(self.currency_prefixes)
        currency_symbols = ''.join([re.escape(i) for i in self.currency_symbol_map])
        currency_tokens = '|'.join([i.replace(' ', '\\s+') for i in self.currency_token_map])
        currency_abbreviations = '|'.join(self.currency_abbr_list)
        trigger_words = '|'.join(self.trigger_words)
        return fr"(?P<text>(?P<prefix>{currency_prefixes}|[{currency_symbols}])\s*(?P<amount>{self.curr_num_ptn})|" \
               fr"(?P<amount>{self.curr_num_ptn})\s*(?P<postfix>{currency_tokens}|{currency_abbreviations})(?:\W|$)|" \
               fr"(?P<amount>{self.curr_num_ptn})\s*(?P<prefix>{currency_prefixes}|[{currency_symbols}])|" \
               fr"(?:\W|^)(?P<trigger_word>{trigger_words})\s[^\d]{{,100}}(?P<amount>\d+(?:\.\d{{1,16}})?))"

    def get_money(self,
                  text: str,
                  return_sources: bool = False,
                  float_digits: int = 4) -> Generator[Union[Tuple[str, str, str], Tuple[str, str]], None, None]:
        for ant in self.get_money_annotations(text, float_digits):
            yield (ant.amount, ant.currency, ant.text) if return_sources else (ant.amount, ant.currency)

    def get_money_annotations(self,
                              text: str,
                              float_digits: int = 4) -> Generator[MoneyAnnotation, None, None]:
        for match in self.currency_ptn_re.finditer(text):
            capture = match.capturesdict()
            if not (capture['prefix'] or capture['postfix']) and not (capture['trigger_word']):
                continue
            prefix = capture['prefix']
            postfix = capture['postfix']
            amount: List[Union[Decimal, Tuple[Decimal, str]]] = \
                list(self.get_amounts(capture['amount'][0], float_digits=float_digits))
            if len(amount) != 1:
                continue
            if prefix:
                prefix = prefix[0].lower()
                currency_type = self.currency_symbol_map.get(prefix) \
                    or self.currency_preffix_map.get(prefix) \
                    or prefix.upper()
            elif postfix:
                postfix = postfix[0].lower()
                currency_type = self.currency_token_map.get(postfix) or (capture['postfix'][0]).upper()
            else:
                currency_type = None
            if not currency_type:
                currency_type = self.default_currency
            text = capture['text'][0].strip(string.punctuation.replace('$', '') + string.whitespace)
            yield MoneyAnnotation(
                locale=self.locale,
                coords=match.span(),
                amount=amount[0],
                text=text,
                currency=currency_type
            )
