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

# Imports
import string

import regex as re
from num2words import num2words

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

# Define small numbers
SMALL_NUMBERS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                 20, 30, 40, 50, 60, 70, 80, 90]
SMALL_NUMBERS_MAP = {num2words(n): n for n in SMALL_NUMBERS}
SMALL_NUMBERS_MAP.update({num2words(n, ordinal=True): n for n in SMALL_NUMBERS})
SMALL_NUMBERS_MAP.update({num2words(n, ordinal=True) + 's': n for n in SMALL_NUMBERS[3:20]})
SMALL_NUMBERS_MAP.update({num2words(n).replace('y', 'ieths'): n for n in SMALL_NUMBERS[20:]})

BIG_NUMBERS_EXPONENT = [3, 6, 9, 12]
MAGNITUDE_MAP = {num2words(10 ** n)[4:]: 10 ** n for n in BIG_NUMBERS_EXPONENT}
MAGNITUDE_MAP.update({'thousandth': 1000, 'thousandths': 1000})

small_numbers = list(SMALL_NUMBERS_MAP.keys())
small_numbers.sort(key=len, reverse=True)
big_numbers = list(MAGNITUDE_MAP.keys())
big_numbers.sort(key=len, reverse=True)

NUM_PTN = r"""
(?:(?:(?:(?:[\.\d][\d\.,]*\s+|\W|^)
(?:(?:{written_small_numbers}|{written_big_numbers}
|hundred(?:th(?:s)?)?|dozen|and|a\s+half|quarters?)[\s-]*)+)
(?:(?:no|\d{{1,2}})/100)?)|(?:[\.\d][\d\.,/]*))(?:\W|$)""".format(
    written_small_numbers='|'.join(small_numbers),
    written_big_numbers='|'.join(big_numbers))
NUM_PTN_RE = re.compile(NUM_PTN, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)
NON_WRIT_RE = re.compile(r'[\d\.]+')
MIXED_WRIT_RE = re.compile(r'(^[\d\.]*)(.+)', re.DOTALL)
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


def text2num(s, search_fraction=True):
    """
    Convert written amount into integer/float.
    :param s: written number
    :param search_fraction: extract fraction
    :return: integer/float
    """
    n = 0
    g = 0
    s = s.lower().replace(',', '').replace('-', ' ').strip(string.whitespace).rstrip(
        string.punctuation + string.whitespace)
    s = re.sub(r'\s+and\s*$|^\s*and\s+', '', s)
    if not (s.startswith('.') and s[1].isdigit()):
        s = s.lstrip(string.punctuation + string.whitespace)

    # if only number or float in string
    if NON_WRIT_RE.fullmatch(s):
        return float(s)

    # if written number has integer/float prefix: "25 million", "2.035 thousand tons"
    if not NUM_FRACTION_RE.fullmatch(s):
        p, s = MIXED_WRIT_RE.search(s).groups()
        g = float(p) if p else 0

    # if written big number has no prefix: "lovely million", "a dozen"
    if ONLY_BIG_WRIT_RE.search(s) and not g:
        s = 'one ' + s

    d = 0
    dnd = NUM_FRACTION_RE.search(s)
    fs = FRACTION_PTN_RE.search(s)
    q = QUARTER_RE.search(s)
    if q:  # convert quarters
        s = QUARTER_RE.sub('', s)
        nu = q.groups()[0]
        d = text2num(nu) / 4
    elif dnd:  # if text has fraction like 1/33 or 87/100 or 1/100
        dn, dd = dnd.groups()
        if dn.isdigit():
            d = int(dn) / int(dd)
        s = NUM_FRACTION_SUB_RE.sub('', s)
    elif fs and search_fraction:  # extract written fractions
        try:
            s = FRACTION_PTN_RE.sub('', s)
            fe = fs.group(0)
            fn, fd = FRACTION_EXTRACT_PTN_RE.search(fe).groups()
            fn = text2num(fn, search_fraction=False)
            fd = text2num(fd, search_fraction=False)
            d = fn / fd
        except (ValueError, TypeError, ZeroDivisionError):
            pass

    # process
    a = s.split()

    x1 = 0
    for w in a:
        if w in ['a', 'and']:
            continue
        x = SMALL_NUMBERS_MAP.get(w, None)
        if x is not None:
            g += x
        elif 'hundred' in w and g != 0:
            g *= 100
        elif w == 'dozen' and g != 0:
            g *= 12
        elif w == 'half':
            if x1:
                g += x1 * .5
            else:
                g += .5
        else:
            x = x1 = MAGNITUDE_MAP.get(w, None)
            if x is not None:
                n += g * x
                g = 0
            else:
                raise RuntimeError('Unknown number: ' + w)
    return n + g + d


def get_amounts(text, return_sources=False, float_digits=4):
    """
    Find possible amount references in the text.
    :param text: text
    :param return_sources: return amount AND source text
    :param float_digits: round float to N digits, don't round if None
    :return: list of amounts
    """
    result = []
    for found_item in NUM_PTN_RE.findall(text):
        if AND_RE.fullmatch(found_item):
            continue
        try:
            amount = text2num(found_item)
        except (AttributeError, RuntimeError, ValueError,
                TypeError, ZeroDivisionError):
            continue
        if isinstance(amount, float) and float_digits:
            amount = round(amount, float_digits)
        if return_sources:
            result.append((amount, found_item.strip()))
        else:
            result.append(amount)
    return result
