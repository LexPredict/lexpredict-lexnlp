"""Regulation extraction for English.

This module implements regulation extraction functionality in English.

Todo:
  * Improved unit tests and case coverage
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

REGULATION_CODES_MAP = {
    'CFR': 'Code of Federal Regulations',
    'USC': 'United States Code',
}

REGULATION_PTN = r"""
(
(\d+)\s*
(U\.?S\.?C\.?|C\.?F\.?R\.?)\s*
(Sec(?:tion|\.)?|§)?\s*
(\d+[\da-zA-Z\-]*)
)"""
REGULATION_PTN_RE = re.compile(REGULATION_PTN, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)

PUBLIC_LAW_PTN = r"""
(
Pub(?:lic|\.)\s+L(?:aw|\.)(?:\s+No.?)?\s+\d+\-\d+
|
\d+\s+Stat\.\s+[\d-]+
)
"""
PUBLIC_LAW_PTN_RE = re.compile(PUBLIC_LAW_PTN, re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)
PUBLIC_LAW_SUB_RE = re.compile(r'.+?(\d+\-\d+)', re.MULTILINE | re.DOTALL)
REGULATIONS_DICT_KEYS = ['regulation_type', 'regulation_code', 'regulation_str']


def get_regulations(text, return_source=False, as_dict=False) -> Generator:
    """
    Get regulations.
    :param text:
    :param return_source:
    :param as_dict:
    :return: tuple or dict
    (volume, reporter, reporter_full_name, page, page2, court, year[, source text])
    """

    for source_text, num1, regulation_type, sec, num2 in REGULATION_PTN_RE.findall(text):
        fixed_regulation_type = regulation_type.replace('.', '')
        if 'sec' in sec.lower():
            sec = 'Section'
        regulation_parts = [num1, fixed_regulation_type, sec, num2] if sec else [num1, fixed_regulation_type, num2]
        item = (REGULATION_CODES_MAP.get(fixed_regulation_type, regulation_type),
                ' '.join(regulation_parts))
        if return_source:
            item += (source_text.strip(),)
        yield {REGULATIONS_DICT_KEYS[n]: val for n, val in enumerate(item)} if as_dict else item

    for source_text in PUBLIC_LAW_PTN_RE.findall(text):
        if 'pub' in source_text.lower():
            fixed_code = PUBLIC_LAW_SUB_RE.sub(r'Public Law No. \1', source_text)
        else:
            fixed_code = ' '.join(source_text.lower().title().split())
        item = ('Public Law', fixed_code)
        if return_source:
            item += (source_text.strip(),)
        yield {REGULATIONS_DICT_KEYS[n]: val for n, val in enumerate(item)} if as_dict else item
