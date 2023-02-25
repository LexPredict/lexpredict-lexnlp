"""Regulation extraction for English.

This module implements regulation extraction functionality in English.

Todo:
  * Improved unit tests and case coverage
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import regex as re

from typing import Dict, Generator, List, Tuple, Union

from lexnlp.extract.common.annotations.regulation_annotation import RegulationAnnotation


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


def get_regulations(
    text: str,
    return_source: bool = False,
    as_dict: bool = False,
) -> Generator[Union[Tuple, Dict], None, None]:
    """
    Get regulations.
    :param text:
    :param return_source:
    :param as_dict:
    :return: tuple or dict
    (volume, reporter, reporter_full_name, page, page2, court, year[, source text])
    """
    for ant in get_regulation_annotations(text):
        if not as_dict:
            item = (ant.source, ant.name)
            if return_source:
                item += (ant.text,)
            yield item
        else:
            yield ant.to_dictionary_legacy()


def get_regulation_list(text: str, return_source: bool = False, as_dict: bool = False) -> List[Union[Tuple, Dict]]:
    """
    """
    return list(get_regulations(text, return_source, as_dict))


def get_regulation_annotations(text: str) -> Generator[RegulationAnnotation, None, None]:
    """
    Get regulations.
    :param text:
    :param return_source:
    :param as_dict:
    :return: tuple or dict
    (volume, reporter, reporter_full_name, page, page2, court, year[, source text])
    """

    for match in REGULATION_PTN_RE.finditer(text):
        source_text, num1, regulation_type, sec, num2 = match.groups()
        fixed_regulation_type = regulation_type.replace('.', '')
        if sec and 'sec' in sec.lower():
            sec = 'Section'
        regulation_parts = [num1, fixed_regulation_type, sec, num2] if sec else [num1, fixed_regulation_type, num2]
        item = (REGULATION_CODES_MAP.get(fixed_regulation_type, regulation_type),
                ' '.join(regulation_parts))

        ant = RegulationAnnotation(coords=match.span(),
                                   source=item[0],
                                   name=item[1],
                                   text=source_text.strip())
        yield ant

    for match in PUBLIC_LAW_PTN_RE.finditer(text):
        source_text = match.groups(0)
        if isinstance(source_text, tuple):
            source_text = source_text[0]
        if source_text and 'pub' in source_text.lower():
            fixed_code = PUBLIC_LAW_SUB_RE.sub(r'Public Law No. \1', source_text)
        else:
            fixed_code = ' '.join(source_text.lower().title().split())

        ant = RegulationAnnotation(coords=match.span(),
                                   source='Public Law',
                                   name=fixed_code,
                                   text=source_text.strip())
        yield ant


def get_regulation_annotation_list(text: str) -> List[RegulationAnnotation]:
    """
    """
    return list(get_regulation_annotations(text))
