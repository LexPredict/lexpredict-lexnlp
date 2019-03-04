"""Court extraction for Spanish.

This module implements extraction functionality for courts in Spain, including formal names, abbreviations,
and aliases.

"""
# pylint: disable=unused-argument

from typing import List, Tuple, Generator, Any
from lexnlp.extract.common.annotations.court_annotation import CourtAnnotation
from lexnlp.extract.en.dict_entities import find_dict_entities, conflicts_take_first_by_id
import os
import re
from lexnlp.extract.common.universal_court_parser import UniversalCourtsParser, ParserInitParams
from lexnlp.extract.es.language_tokens import EsLanguageTokens
from lexnlp.utils.lines_processing.line_processor import LineSplitParams

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def get_courts(text: str,
               court_config_list: List[Tuple[int, str, int, List[Tuple[str, str, bool, int]]]],
               priority: bool = False,
               text_languages: List[str] = None) -> Generator[Tuple[Tuple, Tuple], Any, Any]:
    """
    See lexnlp/extract/en/tests/test_courts.py
    """
    yield from find_dict_entities(text, court_config_list,
                                  conflict_resolving_func=conflicts_take_first_by_id if priority else None,
                                  text_languages=text_languages)


def setup_es_parser():
    ptrs = ParserInitParams()
    ptrs.dataframe_paths = [os.path.join(os.path.dirname(__file__), "../../config/es/es_courts.csv")]
    ptrs.split_ptrs = LineSplitParams()
    ptrs.split_ptrs.line_breaks = {'\n', '.', ';', ','}.union(set(EsLanguageTokens.conjunctions))
    ptrs.split_ptrs.abbreviations = EsLanguageTokens.abbreviations
    ptrs.split_ptrs.abbr_ignore_case = True
    ptrs.court_pattern_checker = re.compile('tribunal', re.IGNORECASE)
    return UniversalCourtsParser(ptrs)


parser = setup_es_parser()


def _get_courts(text: str, language: str = None) -> Generator[dict, None, None]:
    courts = parser.parse(text, language if language else 'es')
    for c in courts:
        yield c.to_dictionary()


def _get_court_list(text: str, language: str = None) -> List[CourtAnnotation]:
    return parser.parse(text, language if language else 'es')
