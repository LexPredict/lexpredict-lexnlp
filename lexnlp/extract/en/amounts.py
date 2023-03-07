"""Amount extraction for English.

This module implements basic amount extraction functionality in English.

This module supports converting:
- numbers with comma delimiter: "25,000.00", "123,456,000"
- written numbers: "Seven Hundred Eighty"
- mixed written numbers: "5 million" or "2.55 BILLION"
- written ordinal numbers: "twenty-fifth"
- fractions (non written): "1/33", "25/100"; where 1 < numerator < 99; 1 < denominator < 999
- fraction No/100 wil be treated as 00/100
- written numbers and fractions: "twenty one AND 5/100"
- written fractions: "one-third", "three tenths", "ten ninety-ninths", "twenty AND one-hundredths",
  "2 hundred and one-thousandth";
   where 1 < numerator < 99 and 2 < denominator < 99 and numerator < denominator;
   or 1 < numerator < 99 and denominator == 100, i.e. 1/99 - 99/100;
   or 1 < numerator < 99 and denominator == 1000, i.e. 1/1000 - 99/1000;
- floats starting with "." (dot): ".5 million"
- "dozen": "twenty-two DOZEN"
- "half": "Six and a HALF Billion", "two and a half"
- "quarter": "five and one-quarter", "5 and one-quarter", "three-quartes"
- multiple numbers: "$25,400, 1 million people and 3.5 tons"

Avoids:
- skip: "5.3.1.", "1/1/2010"
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# pylint: disable=bare-except

import string
from decimal import Decimal, DecimalTuple, InvalidOperation
from typing import Dict, Generator, Optional, Tuple, Union, List

import nltk
import regex as re
from num2words import num2words

from lexnlp.utils.amount_delimiting import infer_delimiters
from lexnlp.extract.common.annotations.amount_annotation import AmountAnnotation


# Define small numbers


SMALL_NUMBERS: List[int] = [*range(0, 21, 1), *range(30, 100, 10)]
SMALL_NUMBERS_MAP = {num2words(n): n for n in SMALL_NUMBERS}
SMALL_NUMBERS_MAP.update({num2words(n, ordinal=True): n for n in SMALL_NUMBERS})
SMALL_NUMBERS_MAP.update({num2words(n, ordinal=True) + 's': n for n in SMALL_NUMBERS[3:20]})
SMALL_NUMBERS_MAP.update({num2words(n).replace('y', 'ieths'): n for n in SMALL_NUMBERS[20:]})
MAGNITUDE_MAP: Dict[str, int] = {
    'k': 1000,
    'thousand': 1000,
    'thousandth': 1000,
    'thousandths': 1000,
    'm': 1000000,
    'mm': 1000000,
    'million': 1000000,
    'b': 1000000000,
    'bil': 1000000000,
    'billion': 1000000000,
    'trill': 1000000000000,
    'trillion': 1000000000000,
}

small_numbers = list(SMALL_NUMBERS_MAP.keys())
small_numbers.sort(key=len, reverse=True)
big_numbers = list(MAGNITUDE_MAP.keys())
big_numbers.sort(key=len, reverse=True)


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

fraction_smb_to_value = {
    '½': 1.0 / 2, '⅓': 1.0 / 3, '⅔': 2.0 / 3,
    '¼': 1.0 / 4, '¾': 3.0 / 4, '⅕': 1.0 / 5,
    '⅖': 2.0 / 5, '⅗': 3.0 / 5, '⅘': 4.0 / 5,
    '⅙': 1.0 / 6, '⅚': 5.0 / 6, '⅐': 1.0 / 7,
    '⅛': 1.0 / 8, '⅜': 3.0 / 8, '⅝': 5.0 / 8,
    '⅞': 7.0 / 8, '⅑': 1.0 / 9, '⅒': 1.0 / 10
}
fraction_smb_to_string = {
    k: str(fraction_smb_to_value[k])[1:]
    for k in fraction_smb_to_value
}

fraction_symbols = ''.join(fraction_smb_to_value)
FRACTION_TAIL = rf'\s{{0,2}}[{fraction_symbols}]+'
FRACTION_TAIL_RE = re.compile(FRACTION_TAIL, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)

NUM_PTN = fr"(?:(?:(?:(?:(?:[\.\d][\d\.,]*\s*|\W|^)(?:(?:{'|'.join(small_numbers)}|{'|'.join(big_numbers)}|hundred" \
          fr"(?:th(?:s)?)?|dozen|and|a\s+half|quarters?)[\s-]*)+)(?:(?:no|\d{{1,2}})/100)?)|(?<=\W|^)" \
          fr"(?:[\.\d][\d\.,'/]*))(?:\W|$))(?:{FRACTION_TAIL})*"

NUM_PTN_RE = re.compile(NUM_PTN, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)

NON_WRIT_RE = re.compile(r'[\d\.]+')
ONLY_DIGITS_AND_DELIMITERS_RE = re.compile(r"[\d.,']+")
BIG_NUMBERS_RE = re.compile(fr"\b({'|'.join(big_numbers)})\b")
MIXED_WRIT_RE = re.compile(r'(^[\d\.,]*)(.+)', re.DOTALL)
ONLY_BIG_WRIT_RE = re.compile(r'^\s*(?:{}|hundred|dozen)'.format('|'.join(MAGNITUDE_MAP)))
NUM_FRACTION_RE = re.compile(r'(\s+no|\d{1,2})/(\d{1,3}[^/])')
NUM_FRACTION_SUB_RE = re.compile(r'(?:\s*and)?(?:\s+no|\s*\d{1,2})/\d{1,3}')
HALF_RE = re.compile(r'\s*and\s+a\s+half')
QUARTER_RE = re.compile(r'(?:\s*and\s+)?(one|two|three)[\s-]+quarters?')
AND_RE = re.compile(r'\W*and\W*', re.IGNORECASE | re.MULTILINE | re.DOTALL)

FRACTION_PTN = r"(?:(?:\W|^)" \
               r"(?:one[\s-]+(?:{writ_ord_2_90}|hundredth|thousandth|(?:{writ_20_90})[\s-]+" \
               r"(?:{writ_ord_1_9})))|" \
               r"(?:(?:{writ_1_90}|[\s-]+)+[\s-]+(?:{writ_ord_3_90_pl}|hundredths|thousandths" \
               r"(?:{writ_20_90})[\s-]+(?:{writ_ord_1_9_pl}))))" \
               r"(?:\W|$)".format(writ_ord_2_90='|'.join([num2words(n, ordinal=True) for n in SMALL_NUMBERS[2:]]),
                                  writ_20_90='|'.join([num2words(n) for n in SMALL_NUMBERS[20:]]),
                                  writ_ord_1_9='|'.join([num2words(n, ordinal=True) for n in SMALL_NUMBERS[1:10]]),
                                  writ_1_90='|'.join([num2words(n) for n in SMALL_NUMBERS[1:]]),
                                  writ_ord_3_90_pl='|'.join([num2words(n, ordinal=True) + 's'
                                                             for n in SMALL_NUMBERS[3:]]),
                                  writ_ord_1_9_pl='|'.join([num2words(n, ordinal=True) + 's'
                                                            for n in SMALL_NUMBERS[1:10]]))
FRACTION_PTN_RE = re.compile(FRACTION_PTN)

FRACTION_EXTRACT_PTN = r"((?:(?:{writ})|(?:(?:{writ_20_90})[\s-]+(?:{writ_1_9}))))[\s-]+" \
                       r"((?:{writ_ord_mix}|(?:(?:{writ_20_90})[\s-]+" \
                       r"(?:{writ_ord_1_9_mix}))|hundredths?|thousandths?))" \
    .format(writ='|'.join([num2words(n) for n in SMALL_NUMBERS[1:]]),
            writ_20_90='|'.join([num2words(n) for n in SMALL_NUMBERS[20:]]),
            writ_1_9='|'.join([num2words(n) for n in SMALL_NUMBERS[1:10]]),
            writ_ord_mix='|'.join([num2words(n, ordinal=True) + 's?' for n in SMALL_NUMBERS[2:]]),
            writ_ord_1_9_mix='|'.join([num2words(n, ordinal=True) + 's?' for n in SMALL_NUMBERS[1:10]]))
FRACTION_EXTRACT_PTN_RE = re.compile(FRACTION_EXTRACT_PTN, re.S | re.M)

# Taken from Su Nam Kim Paper...
grammar = r"""
    NBAR:
        {<NN.*|JJ>*<NN.*>}  # Nouns and Adjectives, terminated with Nouns

    NP:
        {<NBAR>}
        {<NBAR><IN><NBAR>}  # Above, connected with in/of/etc...
"""
chunker = nltk.RegexpParser(grammar)


def cleanup(text) -> str:
    punctuation_and_whitespace: str = \
        string.punctuation + string.whitespace

    text = text \
        .lower() \
        .replace('-', ' ') \
        .strip(string.whitespace) \
        .rstrip(punctuation_and_whitespace)

    text = re.sub(r'\s+and\s*$|^\s*and\s+', '', text)

    if not (
        text.startswith('.')
        and text[1].isdigit()
    ):
        text = text.lstrip(punctuation_and_whitespace)

    # TODO: do not hardcode 'en_US'! This should come from a locale string
    try:
        next(re.finditer(BIG_NUMBERS_RE, text))
        only_digits_and_delimiters: str = \
            next(re.finditer(ONLY_DIGITS_AND_DELIMITERS_RE, text)).captures()[0]
        delimiters: Optional[Dict] = infer_delimiters(only_digits_and_delimiters, 'en_US')
    except StopIteration:
        delimiters: Optional[Dict] = infer_delimiters(text, 'en_US')

    if delimiters is None:
        return text

    group_delimiter = delimiters.get('group_delimiter', False)
    decimal_delimiter = delimiters.get('decimal_delimiter', False)
    if group_delimiter:
        text = text.replace(group_delimiter, '')
    if decimal_delimiter:
        text = text.replace(decimal_delimiter, '.')
    return text


def text2num(
    s: str,
    search_fraction: bool = True,
) -> Optional[Decimal]:
    """
    Convert written amount into Decimal.
    :param s: written number
    :param search_fraction: extract fraction
    :return: Decimal or None
    """
    n: Decimal = Decimal(0)

    # integer/float prefix for a written number
    prefix: Decimal = Decimal(0)

    # pre-process input string
    s: str = cleanup(s)
    if s in ('k', 'm', 'b'):
        return None

    # if only integer or decimal in string
    if NON_WRIT_RE.fullmatch(s):
        return Decimal(s)

    # if written number has integer/float prefix: "25 million", "2.035 thousand tons"
    if not NUM_FRACTION_RE.fullmatch(s):
        p, s = MIXED_WRIT_RE.search(s).groups()
        if p:
            prefix = Decimal(p)

    # if written big number has no prefix: "lovely million", "a dozen"
    if ONLY_BIG_WRIT_RE.search(s) and not prefix:
        s: str = f'one {s}'

    d: Decimal = Decimal(0)
    dnd = NUM_FRACTION_RE.search(s)
    fs = FRACTION_PTN_RE.search(s)
    q = QUARTER_RE.search(s)

    # convert quarters
    if q:
        s: str = QUARTER_RE.sub('', s)
        nu = q.groups()[0]
        d = text2num(nu) / 4

    # if text has a fraction, like 1/33 or 87/100 or 1/100
    elif dnd:
        dn, dd = dnd.groups()
        if dn.isdigit():
            d: Decimal = Decimal(dn) / Decimal(dd)
        s: str = NUM_FRACTION_SUB_RE.sub('', s)

    # extract written fractions
    elif fs and search_fraction:
        try:
            s: str = FRACTION_PTN_RE.sub('', s)
            fe = fs.group(0)
            fn, fd = FRACTION_EXTRACT_PTN_RE.search(fe).groups()
            fn = text2num(fn, search_fraction=False)
            fd = text2num(fd, search_fraction=False)
            d = fn / fd
        except (ValueError, TypeError, ZeroDivisionError):
            pass

    # process
    s_split: List[str] = s.split()

    x1: int = 0
    for token in s_split:
        if token in ('a', 'and'):
            continue
        x: int = SMALL_NUMBERS_MAP.get(token, None)
        if x is not None:
            prefix += x
        elif 'hundred' in token and prefix != 0:
            prefix *= 100
        elif token == 'dozen' and prefix != 0:
            prefix *= 12
        elif token == 'half':
            if x1:
                prefix += (x1 * Decimal(0.5))
            else:
                prefix += Decimal(0.5)
        else:
            x = x1 = MAGNITUDE_MAP.get(token, None)
            if x is not None:
                n += prefix * x
                prefix = Decimal(0)
            else:
                raise RuntimeError(f'Unknown number: {token}')
    return Decimal(n + prefix + d)


def get_np(text) -> Generator[str, None, None]:
    tokens: List[str] = nltk.word_tokenize(text)
    pos_tokens: nltk.tree.Tree = nltk.tag.pos_tag(tokens)
    chunks: nltk.tree.Tree = chunker.parse(pos_tokens)
    for subtree in chunks.subtrees(filter=lambda t: t.label() == 'NP'):
        yield ' '.join(i[0] for i in subtree.leaves())


def quantize_by_float_digit(amount: Decimal, float_digits: int) -> Decimal:
    amount_as_tuple: DecimalTuple = amount.as_tuple()
    exponent: int = amount_as_tuple.exponent
    abs_exponent: int = abs(exponent)
    try:
        if abs_exponent == 0:
            return amount.quantize(Decimal('0.0'))
        if abs_exponent > float_digits:
            if any(amount_as_tuple.digits[exponent:]):
                return amount.quantize(Decimal(f'0.{"0" * float_digits}'))
            return amount.quantize(Decimal('0.0'))
        return amount
    except InvalidOperation as invalid_operation:
        # TODO: fix this problem in a better way later
        # raise InvalidOperation(
        #     f'{amount=}, {float_digits=}, {getcontext().prec=}'
        # ) from invalid_operation
        return amount


def get_amounts(
    text: str,
    return_sources: bool = False,
    extended_sources: bool = True,
    float_digits: int = 4,
) -> Generator[Union[Decimal, Tuple[Decimal, str]], None, None]:
    """
    Find possible amount references in the text.
    :param text: text
    :param return_sources: return amount AND source text
    :param extended_sources: return data around amount itself
    :param float_digits: round float to N digits, don't round if None
    :return: list of amounts
    """
    ant: AmountAnnotation
    for ant in get_amount_annotations(text, extended_sources, float_digits):
        if return_sources:
            yield ant.value, ant.text
        else:
            yield ant.value


def get_amount_list(
    text: str,
    return_sources: bool = False,
    extended_sources: bool = True,
    float_digits: int = 4,
) -> List[Union[Decimal, Tuple[Decimal, str]]]:
    """
    Find possible amount references in the text.
    :param text: text
    :param return_sources: return amount AND source text
    :param extended_sources: return data around amount itself
    :param float_digits: round float to N digits, don't round if None
    :return: list of amounts
    """
    return list(
        get_amounts(
            text=text,
            return_sources=return_sources,
            extended_sources=extended_sources,
            float_digits=float_digits,
        )
    )


def get_amount_annotations(
    text: str,
    extended_sources: bool = True,
    float_digits: int = 4,
) -> Generator[AmountAnnotation, None, None]:
    """
    Find possible amount references in the text.
    :param text: text
    :param extended_sources: return data around amount itself
    :param float_digits: round float to N digits, don't round if None
    :return: list of amounts
    """
    for match in NUM_PTN_RE.finditer(text):  # type: re.Match
        found_item = match.group()
        fraction_tail_items = FRACTION_TAIL_RE.finditer(found_item)
        for fraction_tail in fraction_tail_items:  # type: re.Match
            fraction_tail_smb = fraction_tail.group().strip(' ')
            if fraction_tail_smb in fraction_smb_to_string:
                fraction_ending = fraction_smb_to_string[fraction_tail_smb]
                found_item = found_item[:fraction_tail.span()[0]]
                found_item += fraction_ending
            break

        if AND_RE.fullmatch(found_item):
            continue
        try:
            amount: Optional[Decimal] = text2num(found_item)
        except:
            continue
        if amount is None:
            continue

        if float_digits:
            amount: Decimal = quantize_by_float_digit(
                amount=amount,
                float_digits=float_digits
            )

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

            yield AmountAnnotation(
                coords=match.span(),
                value=amount,
                text=found_item.strip()
            )
        else:
            yield AmountAnnotation(
                coords=match.span(),
                value=amount,
                text=match.group()
            )


def get_amount_annotation_list(
    text: str,
    extended_sources: bool = True,
    float_digits: int = 4,
) -> List[AmountAnnotation]:
    """
    Find possible amount references in the text.
    :param text: text
    :param extended_sources: return data around amount itself
    :param float_digits: round float to N digits, don't round if None
    :return: list of amounts
    """
    return list(
        get_amount_annotations(
            text=text,
            extended_sources=extended_sources,
            float_digits=float_digits,
        )
    )
