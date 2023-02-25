"""Court extraction for Spanish.

This module implements extraction functionality for courts in Spain, including formal names, abbreviations,
and aliases.

"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# pylint: disable=unused-argument

import os
import re
import warnings
from typing import Any, Generator, List, Optional, Tuple

from lexnlp.extract.common.base_path import lexnlp_base_path
from lexnlp.extract.common.annotations.court_annotation import CourtAnnotation
from lexnlp.extract.en.dict_entities import find_dict_entities, conflicts_take_first_by_id, DictionaryEntry, \
    DictionaryEntryAlias
from lexnlp.extract.common.universal_court_parser import UniversalCourtsParser, ParserInitParams
from lexnlp.extract.es.language_tokens import EsLanguageTokens
from lexnlp.utils.lines_processing.line_processor import LineSplitParams
from lexnlp.extract.all_locales.languages import LANG_ES


def _get_courts(
    text: str,
    court_config_list: List[DictionaryEntry],
    priority: bool = False,
    text_languages: Optional[List[str]] = None,
    simplified_normalization: bool = False,
) -> Generator[Tuple[DictionaryEntry, DictionaryEntryAlias], Any, Any]:
    """
    TODO: remove this function
    See lexnlp/extract/en/tests/test_courts.py
    """
    warnings.warn("This function will be removed in a future version of LexNLP", DeprecationWarning)
    for ent in find_dict_entities(
        text,
        court_config_list,
        default_language=LANG_ES.code,
        conflict_resolving_func=conflicts_take_first_by_id if priority else None,
        text_languages=text_languages,
        simplified_normalization=simplified_normalization,
    ):
        yield ent.entity


def setup_es_parser():
    ptrs = ParserInitParams()
    ptrs.dataframe_paths = [os.path.join(lexnlp_base_path, 'lexnlp/config/es/es_courts.csv')]
    ptrs.split_ptrs = LineSplitParams()
    ptrs.split_ptrs.line_breaks = {'\n', '.', ';', ','}.union(set(EsLanguageTokens.conjunctions))
    ptrs.split_ptrs.abbreviations = EsLanguageTokens.abbreviations
    ptrs.split_ptrs.abbr_ignore_case = True
    ptrs.court_pattern_checker = re.compile('tribunal', re.IGNORECASE)
    return UniversalCourtsParser(ptrs)


parser = setup_es_parser()


def get_court_annotations(text: str, language: str = 'es') -> Generator[CourtAnnotation, None, None]:
    yield from parser.parse(text, language)


def get_court_annotation_list(text: str, language: str = 'es') -> List[CourtAnnotation]:
    return list(get_court_annotations(text, language))


def get_courts(text: str, language: str = 'es') -> Generator[dict, None, None]:
    for court_annotation in parser.parse(text, language):
        yield court_annotation.to_dictionary()


def get_court_list(text: str, language: str = 'es') -> List[CourtAnnotation]:
    return list(parser.parse(text, language))
