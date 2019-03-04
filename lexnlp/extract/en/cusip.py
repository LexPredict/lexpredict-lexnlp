"""Ratio extraction for English.

This module implements ratio extraction functionality in English.

Todo:
  * Improved unit tests and case coverage
"""
# Imports
import calendar
import regex as re
import string
from typing import Generator


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

CUSIP_PTN = r"""
(?:\W|^)
(?P<code>
    (?P<issuer_id>\d{2}[\dA-Z]{1}[\dA-Z]{2}[\dA-Z\@\#\*]{1})
    (?P<issue_id>[\dA-Z\@\#\*]{2})
    (?P<checksum>\d{1})
)
(?:\W|$)"""
CUSIP_PTN_RE = re.compile(CUSIP_PTN, re.VERBOSE | re.DOTALL)

INTERNAL_ISSUER_ID_PTN = r"""
(?:\d{3}99[\dA-Z]|99\d{3}[\dA-Z])
"""
INTERNAL_ISSUER_ID_PTN_RE = re.compile(INTERNAL_ISSUER_ID_PTN, re.VERBOSE)

PPN_PTN_RE = re.compile(r'[\@\#\*]')

TBA_PTN =  r"""
(?P<product_code>\d{2})
(?P<mortgage_type>[A-Z]{1})
(?P<coupon>\d{3})
(?P<maturity>\d{1})
(?P<settlement_month>\d{1})
(?P<checksum>\d{1})
"""
TBA_PTN_RE = re.compile(TBA_PTN, re.VERBOSE)
TBA_MONTHS = {i: calendar.month_name[n+1] for n, i in enumerate('123456789ABC')}

CHECKSUM_BASE = {i: 10+n for n, i in enumerate(string.ascii_uppercase)}
CHECKSUM_BASE.update({'*': 36, '@': 37, '#': 38})


def is_cusip_valid(code, return_checksum=False):
    code, _checksum = code[:8], int(code[8])
    sum = 0
    for pos, char in enumerate(code, start=1):
        if char.isdigit():
            num = int(char)
        elif char in CHECKSUM_BASE:
            num = CHECKSUM_BASE[char]
        else:
            return False
        if pos % 2 == 0:
            num *= 2
        sum += int(num / 10) + num % 10
    checksum = (10 - sum % 10) % 10
    if return_checksum:
        return checksum
    return checksum == _checksum


def get_cusip(text) -> Generator:
    """
    INFO: https://www.cusip.com/pdf/CUSIP_Intro_03.14.11.pdf
    """
    for match in CUSIP_PTN_RE.finditer(text):
        capture = match.capturesdict()
        code = ''.join(capture['code'])
        issuer_id = ''.join(capture['issuer_id'])
        issue_id = ''.join(capture['issue_id'])
        checksum = int(capture['checksum'][0])
        ppn = False

        # validate CUSIP
        if not is_cusip_valid(code):
            continue

        tba = TBA_PTN_RE.fullmatch(code)
        if tba:
            tba = tba.groupdict()
            settlement_month_name = TBA_MONTHS.get(tba['settlement_month'])
            # if not settlement_month_name:
            #     continue
            tba['settlement_month_name'] = settlement_month_name
        elif PPN_PTN_RE.search(code):
            ppn = True

        yield {'location_start': match.start(1),
               'location_end': match.end(1),
               'text': code,
               'issuer_id': issuer_id,
               'issue_id': issue_id,
               'checksum': checksum,
               'internal': bool(INTERNAL_ISSUER_ID_PTN_RE.match(issuer_id)),
               'tba': tba,
               'ppn': ppn}


def get_cusip_list(text):
    return list(get_cusip(text))
