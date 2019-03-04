"""Amount extraction for German.

This module implements amount extraction functionality in German.

Todo:
  * Improved unit tests and case coverage
"""
# pylint: disable=broad-except

import string
from typing import Generator

import nltk
import regex as re
from num2words import num2words, CONVERTER_CLASSES


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
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
CURRENCY_PREFIX_MAP = {
    "chf": "CHF",
    "rmb": "CNY",
}
allowed_prev_units = list(CURRENCY_SYMBOL_MAP) + list(CURRENCY_PREFIX_MAP)

grammar = r"""
    NBAR:
        {<NN.*|JJ>*<NN.*>}  # Nouns and Adjectives, terminated with Nouns
    NP:
        {<NBAR>}
        {<NBAR><IN><NBAR>}  # Above, connected with in/of/etc...
"""
chunker = nltk.RegexpParser(grammar)


def get_np(text) -> Generator:
    tokens = nltk.word_tokenize(text)
    pos_tokens = nltk.tag.pos_tag(tokens)
    chunks = chunker.parse(pos_tokens)
    for subtree in chunks.subtrees(filter=lambda t: t.label() == 'NP'):
        np = ' '.join([i[0] for i in subtree.leaves()])
        yield np


class AmountParserDE(object):
    QUARTER = 'viertel'

    def __init__(self):

        self.language = 'de'

        N2W_CONFIG = CONVERTER_CLASSES[self.language]

        self.BIG_NUMBERS_EXPONENT = [3, 6, 9, 12]
        self.ONE = N2W_CONFIG.low_numwords[-2]
        self.HUNDRED = dict(N2W_CONFIG.mid_numwords)[100]

        UNIQUE_NUMBERS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                          20, 30, 40, 50, 60, 70, 80, 90,
                          100, 1000, 1000000, 1000000000, 1000000000000]
        UNIQUE_NUMBERS_MAP = {num2words(n, ordinal=True, lang=self.language).replace('eine ', ''): n
                              for n in UNIQUE_NUMBERS}
        UNIQUE_NUMBERS_MAP.update(
            {num2words(n, lang=self.language).replace('eine ', ''): n for n in UNIQUE_NUMBERS})
        UNIQUE_NUMBERS_MAP.update(
            {'ein': 1,
             'eine': 1,
             'einen': 1,
             'einhalb': 0.5,
             'millionen': 1000000,
             'millionenste': 1000000,
             'milliarden': 1000000000,
             'milliardenste': 1000000000})

        self.UNIQUE_NUMBERS_MAP = UNIQUE_NUMBERS_MAP

        self.MAGNITUDE_MAP = {num2words(10 ** n, lang=self.language).replace('eine ', ''): 10 ** n
                              for n in self.BIG_NUMBERS_EXPONENT}
        self.MAGNITUDE_MAP.update(
            {'millionen': 1000000,
             'millionenste': 1000000,
             'milliarden': 1000000000,
             'milliardenste': 1000000000,
             'halbe': 0.5,
             'k': 1000,
             'm': 1000000,
             'b': 1000000000})

        unique_number_list = list(self.UNIQUE_NUMBERS_MAP.keys())
        unique_number_list.sort(key=len, reverse=True)
        self.UNIQUE_NUMBER_SPLIT_RE = re.compile(r'({}|\s+)'.format('|'.join(unique_number_list)))

        self.NUM_PTN = r"""
        (?:
        (?:[\.\d][\d\.,]*\s+|\W|^)
        (?:(?:(?:in)?viertel|halbe|{written_unique_numbers}|und)\s?)+(?:\W|$)|
        (?:[\.\d][\d\.,\s]*)
        )
        """.format(written_unique_numbers='|'.join(unique_number_list))
        self.NUM_PTN_RE = re.compile(self.NUM_PTN,
                                     re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)

        self.NON_WRIT_RE = re.compile(r'[\d\.,\s]+')

        self.MIXED_WRIT_RE = re.compile(r'(^[\d\.]*)(.+)', re.DOTALL)

        self.QUARTER_RE = re.compile(r'(?:\s*und\s+)?(ein|eine|zwei|drei)\s*viertel')

        self.WRONG_FULLMATCH_RE = re.compile(r'\W*und\W*|\W+', re.IGNORECASE | re.MULTILINE | re.DOTALL)

    def cleanup(self, text):
        text = text.lower().replace(',', '.').replace('-', ' ').strip(string.whitespace).rstrip(
            string.punctuation + string.whitespace)
        if not (text.startswith('.') and text[1].isdigit()):
            text = text.lstrip(string.punctuation + string.whitespace)
        return text

    def split(self, text):
        return [i for i in self.UNIQUE_NUMBER_SPLIT_RE.split(text) if i not in ['', ' ']]

    def text2num(self, s):
        """
        Convert written amount into integer/float.
        :param s: written number
        :param search_fraction: extract fraction
        :return: integer/float
        """
        n = 0
        g = 0
        s = self.cleanup(s)

        # if only number or float in string
        if self.NON_WRIT_RE.fullmatch(s):
            return float(s.replace(' ', ''))

        # if written number has integer/float prefix: "25 million", "2.035 thousand tons"
        if self.MIXED_WRIT_RE.search(s):
            p, s = self.MIXED_WRIT_RE.search(s).groups()
            g = float(p) if p else 0

        d = 0
        # TODO: extract fractions, half, quarter

        # convert quarters
        if self.QUARTER_RE and self.QUARTER_RE.search(s):
            nu = self.QUARTER_RE.search(s).groups()[0]
            d = self.text2num(nu) / 4
            s = self.QUARTER_RE.sub('', s)

        # process
        a = self.split(s)

        for w in a:
            if w == 'und':
                continue

            x = self.UNIQUE_NUMBERS_MAP.get(w, None)
            if self.HUNDRED in w and g != 0:
                g *= 100

            elif w in self.MAGNITUDE_MAP:
                x = self.MAGNITUDE_MAP.get(w, None)
                if w == 'halbe':
                    g = 0.5
                    continue
                n += (g or 1) * x
                g = 0

            elif x is None:
                raise RuntimeError('Unknown number: ' + w)

            else:
                g += x

        return n + g + d

    def parse(self, text, return_sources=False, extended_sources=True, float_digits=4) -> Generator:
        """
        Find possible amount references in the text.
        :param text: text
        :param return_sources: return amount AND source text
        :param extended_sources: return data around amount itself
        :param float_digits: round float to N digits, don't round if None
        :return: list of amounts
        """
        for match in self.NUM_PTN_RE.finditer(text):
            found_item = match.group()
            if self.WRONG_FULLMATCH_RE.fullmatch(found_item):
                continue
            try:
                amount = self.text2num(found_item)
            except Exception as e:
                print(e)
                continue
            if amount is None:
                continue
            if isinstance(amount, float) and float_digits:
                amount = round(amount, float_digits)
            if return_sources:
                if extended_sources:
                    unit = ''
                    next_text = text[match.span()[1]:]
                    if next_text:
                        for np in get_np(next_text):
                            if next_text.startswith(np):
                                unit = np
                        if unit:
                            found_item = ' '.join([found_item.strip(), unit])
                    if not unit:
                        prev_text = text[:match.span()[0]]
                        prev_text_tags = nltk.word_tokenize(prev_text)
                        if prev_text_tags and prev_text_tags[-1].lower() in allowed_prev_units:
                            sep = ' ' if text[match.span()[0] - 1] == ' ' else ''
                            found_item = sep.join([prev_text_tags[-1], found_item.rstrip()])
                yield (amount, found_item.strip(), match.span())
                # yield (amount, found_item.strip())
            else:
                yield amount


get_amounts = AmountParserDE().parse


def get_amount_list(*args, **kwargs):
    return list(get_amounts(*args, **kwargs))
