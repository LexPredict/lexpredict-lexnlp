"""PII extraction for English.

This module implements PII extraction functionality in English.

Todo:
  * http://www.doncio.navy.mil/contentview.aspx?id=2428
"""
# Imports
import regex as re
from typing import Generator

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

SSN_PATTERN = r"""
(?P<block1>[0-9]{3})[\-]?(?P<block2>[0-9]{2})[\-]?(?P<block3>[0-9]{4})
"""
RE_SSN = re.compile(SSN_PATTERN, re.IGNORECASE | re.UNICODE | re.DOTALL | re.VERBOSE)

US_PHONE_PATTERN = r"""
[\(]?(?P<area_code>[0-9]{3})[\)]?
[\-\s]+
(?P<exchange>[0-9]{3})
[\-\s]+
(?P<last4>[0-9]{4})
"""
RE_US_PHONE = re.compile(US_PHONE_PATTERN, re.IGNORECASE | re.UNICODE | re.DOTALL | re.VERBOSE)


def get_ssns(text, return_sources=False) -> Generator:
    """
    Find possible SSN references in the text.
    :param text:
    :param return_sources:
    :return:
    """

    # Iterate through all potential matches
    for match in RE_SSN.finditer(text):
        # Get individual group matches
        captures = match.capturesdict()
        ssn = "{block1}-{block2}-{block3}".format(block1=captures["block1"].pop(),
                                                  block2=captures["block2"].pop(),
                                                  block3=captures["block3"].pop(),
                                                  )

        if return_sources:
            yield ssn, match.group()
        else:
            yield ssn


def get_us_phones(text, return_sources=False) -> Generator:
    """
    Find possible SSN references in the text.
    :param text:
    :param return_sources:
    :return:
    """

    # Iterate through all potential matches
    for match in RE_US_PHONE.finditer(text):
        # Get individual group matches
        captures = match.capturesdict()
        phone = "({area_code}) {exchange}-{last4}".format(area_code=captures["area_code"].pop(),
                                                          exchange=captures["exchange"].pop(),
                                                          last4=captures["last4"].pop(),
                                                          )

        if return_sources:
            yield phone, match.group()
        else:
            yield phone


def get_pii(text, return_sources=False) -> Generator:
    """
    Find possible PII references in the text.
    :param text:
    :param return_sources:
    :return:
    """

    for ssn in get_ssns(text, return_sources):
        if isinstance(ssn, tuple) or isinstance(ssn, list):
            row = ['ssn']
            for v in ssn:
                row.append(v)
            yield tuple(row)
        else:
            yield ('ssn', ssn)

    for phone in get_us_phones(text, return_sources):
        if isinstance(phone, tuple) or isinstance(phone, list):
            row = ['us_phone']
            for v in phone:
                row.append(v)
            yield tuple(row)
        else:
            yield ('us_phone', phone)
