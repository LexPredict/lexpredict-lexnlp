"""Amount extraction for German.

This module implements amount extraction functionality in German.

Todo:
  * Improved unit tests and case coverage
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# pylint: disable=broad-except

import nltk
import string
import regex as re
from decimal import Decimal
from typing import Dict, Generator, List, Optional, Union
from num2words import num2words, CONVERTER_CLASSES
from lexnlp.extract.common.annotations.amount_annotation import AmountAnnotation
from lexnlp.extract.en.amounts import quantize_by_float_digit
from lexnlp.utils.amount_delimiting import infer_delimiters


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


class AmountParserDE:
    QUARTER = 'viertel'

    def __init__(self):

        self.language = 'de'

        N2W_CONFIG = CONVERTER_CLASSES[self.language]

        self.BIG_NUMBERS_EXPONENT = [3, 6, 9, 12]
        self.ONE = N2W_CONFIG.low_numwords[-2]
        self.HUNDRED = dict(N2W_CONFIG.mid_numwords)[100]

        UNIQUE_NUMBERS: List[int] = [*range(0, 21, 1), *range(30, 100, 10)]
        BIG_UNIQUE_NUMBERS: List[int] = [100, 1000, 1000000, 1000000000, 1000000000000]

        UNIQUE_NUMBERS_MAP: Dict = {}
        # ordinal
        UNIQUE_NUMBERS_MAP.update(
            {num2words(n, ordinal=True, lang=self.language): n for n in UNIQUE_NUMBERS})
        UNIQUE_NUMBERS_MAP.update(
            {num2words(n, ordinal=True, lang=self.language).replace('eine ', '').replace('ein', '').lower(): n
             for n in BIG_UNIQUE_NUMBERS})
        # non-ordinal
        UNIQUE_NUMBERS_MAP.update(
            {num2words(n, lang=self.language): n for n in UNIQUE_NUMBERS})
        UNIQUE_NUMBERS_MAP.update(
            {num2words(n, lang=self.language).replace('eine ', '').replace('ein', '').lower(): n
             for n in BIG_UNIQUE_NUMBERS})
        # addon
        UNIQUE_NUMBERS_MAP.update({
            'ein': 1,
            'eine': 1,
            'einen': 1,
            'einhalb': Decimal(0.5),
            'millionen': 1000000,
            'millionenste': 1000000,
            'milliarden': 1000000000,
            'milliardenste': 1000000000
        })

        self.UNIQUE_NUMBERS_MAP: Dict[str, Union[int, Decimal]] = UNIQUE_NUMBERS_MAP

        self.MAGNITUDE_MAP = {num2words(10 ** n, lang=self.language).replace('eine ', '').replace('ein', '').lower(): 10 ** n
                              for n in self.BIG_NUMBERS_EXPONENT}
        self.MAGNITUDE_MAP.update({
            'millionen': 1000000,
            'millionenste': 1000000,
            'milliarden': 1000000000,
            'milliardenste': 1000000000,
            'halbe': Decimal(0.5),
            'k': 1000,
            'm': 1000000,
            'b': 1000000000,
        })

        unique_number_list: List[str] = list(self.UNIQUE_NUMBERS_MAP.keys())
        unique_number_list.sort(key=len, reverse=True)
        self.UNIQUE_NUMBER_SPLIT_RE = re.compile(r'({}|\s+)'.format('|'.join(unique_number_list)))

        self.NUM_PTN = r"""
        (?:
            (?:\d+(?:[,.]\d+)*\s+|\W|^)?
            \b(?:(?:(?:in)?viertel|halbe|{written_unique_numbers}|und)\s?)+(?:\W|$)
        |
            (?:[\.\d][\d\.,'\s]*)
        )
        """.format(written_unique_numbers='|'.join(unique_number_list))
        self.NUM_PTN_RE = re.compile(self.NUM_PTN, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)

        self.NON_WRIT_RE = re.compile(r'[\d\.,\s]+')

        self.MIXED_WRIT_RE = re.compile(r'(^[\d\.,]*)(.+)', re.DOTALL)

        self.QUARTER_RE = re.compile(r'(?:\s*und\s+)?(ein|eine|zwei|drei)\s*viertel')

        self.WRONG_FULLMATCH_RE = re.compile(r'\W*und\W*|\W+', re.IGNORECASE | re.MULTILINE | re.DOTALL)

    @staticmethod
    def cleanup(text) -> str:

        punctuation_and_whitespace: str = \
            string.punctuation + string.whitespace

        text = text \
            .lower() \
            .strip(string.whitespace) \
            .rstrip(punctuation_and_whitespace)

        if not (
            text.startswith('.')
            and text[1].isdigit()
        ):
            text = text.lstrip(punctuation_and_whitespace)

        # TODO: do not hardcode 'de_DE'! This should come from a locale string
        delimiters: Optional[Dict] = infer_delimiters(text, 'de_DE')
        if delimiters is None:
            return text

        group_delimiter = delimiters.get('group_delimiter', False)
        decimal_delimiter = delimiters.get('decimal_delimiter', False)
        if group_delimiter:
            text = text.replace(group_delimiter, '')
        if decimal_delimiter:
            text = text.replace(decimal_delimiter, '.')
        return text

    def split(self, text):
        return [i for i in self.UNIQUE_NUMBER_SPLIT_RE.split(text) if i not in ['', ' ']]

    def text2num(self, s: str):
        """
        Convert written amount into integer/float.
        :param s: written number
        :param search_fraction: extract fraction
        :return: integer/float
        """
        n: Decimal = Decimal(0)
        g: Decimal = Decimal(0)
        s = self.cleanup(s)

        # if only number or float in string
        if self.NON_WRIT_RE.fullmatch(s):
            return Decimal(s.replace(' ', ''))

        # if written number has integer/float prefix: "25 million", "2.035 thousand tons"
        if self.MIXED_WRIT_RE.search(s):
            p, s = self.MIXED_WRIT_RE.search(s).groups()
            g: Decimal = \
                Decimal(p.rstrip(string.punctuation + string.whitespace))\
                if p else Decimal(0)

        d: Decimal = Decimal(0)
        # TODO: extract fractions, half, quarter

        # convert quarters
        if self.QUARTER_RE and self.QUARTER_RE.search(s):
            nu = self.QUARTER_RE.search(s).groups()[0]
            d = self.text2num(nu) / 4
            s = self.QUARTER_RE.sub('', s)

        # process
        a: List = self.split(s)

        for w in a:
            if w == 'und':
                continue

            x = self.UNIQUE_NUMBERS_MAP.get(w, None)
            if self.HUNDRED in w and g != 0:
                g *= Decimal(100)

            elif w in self.MAGNITUDE_MAP:
                x = self.MAGNITUDE_MAP.get(w, None)
                if w == 'halbe':
                    g = Decimal(0.5)
                    continue
                n += Decimal(g or 1) * x
                g = Decimal(0)

            elif x is None:
                raise RuntimeError('Unknown number: ' + w)

            else:
                g += x

        return n + g + d

    def parse(
        self,
        text: str,
        return_sources: bool = False,
        extended_sources: bool = True,
        float_digits: int = 4
    ) -> Generator:
        """
        Find possible amount references in the text.
        :param text: text
        :param return_sources: return amount AND source text
        :param extended_sources: return data around amount itself
        :param float_digits: round float to N digits, don't round if None
        :return: list of amounts
        """
        for ant in self.parse_annotations(text, float_digits, return_sources):
            if not return_sources:
                yield ant.value
            else:
                if extended_sources:
                    yield ant.value, ant.text, ant.coords
                else:
                    yield ant.value, ant.text

    def parse_annotations(
        self,
        text: str,
        float_digits: int = 4,
        return_sources: bool = True
    ) -> Generator[AmountAnnotation, None, None]:
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
            if float_digits:
                amount: Decimal = quantize_by_float_digit(
                    amount=amount,
                    float_digits=float_digits
                )

            ant = AmountAnnotation(coords=match.span(),
                                   value=amount,
                                   locale=self.language)

            if return_sources:
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

                ant.text = found_item.strip()
            yield ant


amount_parser = AmountParserDE()


get_amounts = amount_parser.parse


get_amount_annotations = amount_parser.parse_annotations


def get_amount_list(
    text: str,
    return_sources: bool = False,
    extended_sources: bool = True,
    float_digits: int = 4
):
    return list(get_amounts(text, return_sources, extended_sources, float_digits))


def get_amount_annotation_list(
    text: str,
    float_digits: int = 4,
    return_sources: bool = True
) -> List[AmountAnnotation]:
    return list(get_amount_annotations(text, float_digits, return_sources))
