"""Court extraction for English.

This module implements extraction functionality for courts in English, including formal names, abbreviations,
and aliases.

Todo:
  * Add utilities for loading court data
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
from typing import List, Tuple, Generator, Any

from lexnlp.extract.all_locales.languages import LANG_EN
from lexnlp.extract.common.base_path import lexnlp_base_path
from lexnlp.extract.common.annotations.court_annotation import CourtAnnotation
from lexnlp.extract.en.dict_entities import find_dict_entities, conflicts_take_first_by_id, DictionaryEntry, \
    DictionaryEntryAlias
from lexnlp.extract.common.universal_court_parser import UniversalCourtsParser, ParserInitParams
from lexnlp.extract.en.en_language_tokens import EnLanguageTokens
from lexnlp.utils.lines_processing.line_processor import LineSplitParams


def _get_courts(
    text: str,
    court_config_list: List[DictionaryEntry],
    priority: bool = False,
    text_languages: List[str] = None,
    simplified_normalization: bool = False
) -> Generator[Tuple[DictionaryEntry, DictionaryEntryAlias], Any, Any]:
    """
    TODO: remove this function
    Searches for courts from the provided config list and yields tuples of (court_config, court_alias).
    Court config is: (court_id, court_name, [list of aliases])
    Alias is: (alias_text, language, is_abbrev, alias_id)

    This method uses general searching routines for dictionary entities from dict_entities.py module.
    Methods of dict_entities module can be used for comfortable creating the config: entity_config(),
    entity_alias(), add_aliases_to_entity().
    :param text:
    :param court_config_list: List of all possible known courts in the form of tuples:
     (id, name, [(alias, lang, is_abbrev], ...).
    :param priority: If two courts found with the totally equal matching aliases - then use the one with the lowest id.
    :param text_languages: Language(s) of the source text. If a language is specified then only aliases of this
    language will be searched for. For example: this allows ignoring "Island" - a German language
     alias of Iceland for English texts.
    :param simplified_normalization: don't use NLTK for just "normalizing" the text
    :return: Generates tuples: (court entity, court alias)
    """
    warnings.warn("This function will be removed in a future version of LexNLP", DeprecationWarning)
    for ent in find_dict_entities(text,
                                  court_config_list,
                                  default_language=LANG_EN.code,
                                  conflict_resolving_func=conflicts_take_first_by_id if priority else None,
                                  text_languages=text_languages,
                                  simplified_normalization=simplified_normalization):
        yield ent.entity


def setup_en_parser():
    ptrs = ParserInitParams()
    file_path = os.path.join(lexnlp_base_path, 'lexnlp/config/en')
    ptrs.dataframe_paths = ['us_state_courts.csv',
                            'us_courts.csv',
                            'ca_courts.csv',
                            'au_courts.csv']
    ptrs.dataframe_paths = [os.path.join(file_path, p)
                            for p in ptrs.dataframe_paths]

    ptrs.split_ptrs = LineSplitParams()
    ptrs.split_ptrs.line_breaks = {'\n', '.', ';', ','}.union(set(EnLanguageTokens.conjunctions))
    ptrs.split_ptrs.abbreviations = EnLanguageTokens.abbreviations
    ptrs.split_ptrs.abbr_ignore_case = True
    ptrs.court_pattern_checker = re.compile('court', re.IGNORECASE)
    return UniversalCourtsParser(ptrs)


parser = setup_en_parser()


def get_court_annotations(text: str, language: str = 'en') -> Generator[CourtAnnotation, None, None]:
    yield from parser.parse(text, language)


def get_court_annotation_list(text: str, language: str = 'en') -> List[CourtAnnotation]:
    return list(parser.parse(text, language))


def get_courts(text: str, language: str = 'en') -> Generator[dict, None, None]:
    for court_annotation in parser.parse(text, language):
        yield court_annotation.to_dictionary()


def get_court_list(text: str, language: str = 'en') -> List[CourtAnnotation]:
    return list(parser.parse(text, language))
